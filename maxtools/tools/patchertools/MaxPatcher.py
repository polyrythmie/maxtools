# -*- coding: utf-8 -*-
from abjad import attach
from abjad import inspect_
from abjad.tools.abctools.AbjadObject import AbjadObject
from abjad.tools import durationtools
from abjad.tools import selectortools
from abjad.tools import scoretools
import collections
import itertools
from maxtools.tools.cuetools.Cue import Cue
from maxtools.tools.cuetools.CueCommand import CueCommand

class MaxPatcher(AbjadObject):

    ### CLASS VARIABLES ###

    __slots__ = (
        '_context',
        '_context_name',
        '_command_point_map',
        '_cue_voice',
        '_cues',
        '_file_name',
        '_initialization',
        '_previous_segment_metadata',
        '_routers',
        '_segment_metadata',
        )

    ### INITIALIZER ###

    def __init__(
        self,
        file_name,
        context_name,
        routers,
        initialization=None,
        ):
        self._file_name = file_name
        self._context_name = context_name
        if not isinstance(routers, (list, tuple)):
            routers = (routers,)
        self._routers = routers
        if not isinstance(initialization, (list, tuple)):
            initialization = (initialization,)
        self._initialization = initialization

    ### SPECIAL METHODS ###

    def __call__(
        self,
        segment_maker=None,
        score=None,
        segment_metadata=None,
        meters=None,
        meters_as_timespans=None,
        previous_segment_metadata=None,
        ):
        if segment_maker is not None:
            score = segment_maker._score
            self._segment_metadata = segment_maker._segment_metadata
            self._previous_segment_metadata = segment_maker._previous_segment_metadata
            meters_as_timespans = segment_maker.meters_to_timespans(segment_maker._meters)
        else:
            assert score is not None
            self._segment_metadata = segment_metadata or collections.OrderedDict()
            self._previous_segment_metadata = previous_segment_metadata or collections.OrderedDict()
        assert self.context_name in score
        self._context = score[self.context_name]
        meters_as_timespans = meters_as_timespans or self._get_meters_as_timespans(self._context, meters=meters)

        last_cue_time_context_map = self._previous_segment_metadata.get('last_cue_time_context_map', {})
        last_cue_time = last_cue_time_context_map.get(self.context_name, [0, 0])
        last_cue_number = last_cue_time[0]
        last_cue_time_to_segment_end = last_cue_time[1]

        initialization = self.initialization if last_cue_number == 0 else []
        self._command_point_map = self._collect_command_points(self._context, self.routers, initialization=initialization)
        self._cue_voice = self._make_cue_voice(meters_as_timespans, self._command_point_map)
        self._insert_cue_voice()
        self._cues = self._attach_cues(self._cue_voice, last_cue_number, last_cue_time_to_segment_end)
        self._update_segment_metadata()
        return self._cue_file, self._segment_metadata

    ### PRIVATE METHODS ###

    @staticmethod
    def _collect_command_points(
        context,
        routers,
        initialization=[],
        ):
        result = {}
        for router in routers:
            for start_offset, commands in router._collect_command_points(context, initialization=initialization).iteritems():
                if not start_offset in result:
                    result[start_offset] = []
                result[start_offset].extend(commands)
        return result

    @staticmethod
    def _attach_cues(
        cue_voice,
        last_cue_number=0,
        last_cue_time_to_segment_end=0,
        ):
        make_cue_at = []
        for index, measure in enumerate(cue_voice):
            for subindex, leaf in enumerate(measure):
                if not all([x.automatic for x in inspect_(leaf).get_indicators(prototype=CueCommand)]):
                    make_cue_at.append([index, subindex])
        if not make_cue_at:
            return
        current_cue_number = last_cue_number + 1
        cues = []
        last_indices = [0, 0]
        selector = selectortools.Selector().by_leaf().flatten()
        selection = selector(cue_voice)._music
        for index, indices in enumerate(make_cue_at):
            if index is 0 and indices != [0, 0] and last_cue_number != 0:
                reminder_cue = Cue(number=last_cue_number, reminder=True)
                cues.append(reminder_cue)
            if cues:
                attach(cues[-1], selection[selection.index(cue_voice[last_indices[0]][last_indices[1]]):selection.index(cue_voice[indices[0]][indices[1]])])
            new_cue = Cue(number=current_cue_number)
            cues.append(new_cue)
            current_cue_number += 1
            last_indices = indices
            if index == len(make_cue_at) - 1:
                attach(cues[-1], selection[selection.index(cue_voice[last_indices[0]][last_indices[1]]):])
        return cues

    @staticmethod
    def _get_meters_as_timespans(context, meters=None):
        # Copied from consort.tools.SegmentMaker so as not to require the library
        # if the user is not using it.
        from abjad.tools import metertools, mathtools, timespantools
        if meters is None:
            meters = []
            selector = selectortools.Selector().by_class(prototype=scoretools.Voice).flatten()
            selection = max(selector(context))
            selector = selectortools.Selector().by_leaf().by_logical_measure()
            selection = selector(selection)
            for select in selection:
                meters.append(metertools.Meter(select.get_duration()))
        durations = [_.duration for _ in meters]
        offsets = mathtools.cumulative_sums(durations)
        offsets = [durationtools.Offset(_) for _ in offsets]
        timespans = []
        for i, meter in enumerate(meters):
            start_offset = offsets[i]
            stop_offset = offsets[i + 1]
            timespan = timespantools.AnnotatedTimespan(
                annotation=meter,
                start_offset=start_offset,
                stop_offset=stop_offset,
                )
            timespans.append(timespan)
        return timespans

    def _insert_cue_voice(
        self,
        ):
        self._context.insert(0, self._cue_voice)

    @staticmethod
    def _make_cue_voice(
        timespans,
        command_point_map,
        ):
        def make_skip_from(start_offset, stop_offset):
            duration = stop_offset - start_offset
            if duration > durationtools.Duration(0):
                multiplier, duration = duration.yield_equivalent_durations()[0]
                skip = scoretools.Skip(duration)
                attach(multiplier, skip)
                return skip
            return None

        def make_note_from(start_offset, stop_offset):
            duration = stop_offset - start_offset
            if duration > durationtools.Duration(0):
                multiplier, duration = duration.yield_equivalent_durations()[0]
                note = scoretools.Note(0, duration)
                attach(multiplier, note)
                return note
            return None

        measures = []
        for time_signature, group in itertools.groupby(timespans, lambda x: x.annotation.implied_time_signature):
            containers = []
            for timespan in group:
                timespan_start_offset, timespan_stop_offset = timespan.offsets
                offsets_in_timespan = sorted([start_offset for start_offset in command_point_map if timespan_start_offset <= start_offset < timespan_stop_offset])
                if not offsets_in_timespan:
                    containers.append([])
                else:
                    contents = []
                    initial_skip = make_skip_from(timespan_start_offset, offsets_in_timespan[0])
                    if initial_skip is not None:
                        contents.append(initial_skip)
                    for index, offset in enumerate(offsets_in_timespan):
                        if index == (len(offsets_in_timespan) - 1):
                            note = make_note_from(offset, timespan_stop_offset)
                        else:
                            note = make_note_from(offset, offsets_in_timespan[index + 1])
                        for cue_command in command_point_map[offset]:
                            attach(cue_command, note)
                        contents.append(note)
                    containers.append(contents)
            for container, subgroup in itertools.groupby(containers, lambda x: x):
                if not container:
                    skip = scoretools.Skip(1)
                    multiplier = durationtools.Multiplier(time_signature) * len(tuple(subgroup))
                    attach(multiplier, skip)
                    container = [skip]
                measure = scoretools.Measure(time_signature=time_signature, music=container)
                measures.append(measure)
        cue_voice = scoretools.Voice(measures)
        return cue_voice

    def _update_segment_metadata(self):
        if not self._segment_metadata.get('last_cue_time_context_map', {}):
            self._segment_metadata.update(
                last_cue_time_context_map=collections.OrderedDict()
                )
        last_cue_time_context_map = self._segment_metadata.get('last_cue_time_context_map', {})
        last_cue_time_context_map.update({self.context_name:[self._cues[-1].number, self._cues[-1]._duration_in_ms]})

    ### PRIVATE PROPERTIES ###

    @property
    def _cue_file(self):
        result = []
        if self._cues[0].number == 1:
            init_commands = set()
            for router in self._routers:
                init_commands |= router._get_initialization_commands()
            for init_command in init_commands:
                result.append('0 {}'.format(init_command._cue_format))
        for cue in self._cues:
            result.append(cue._cue_file_format)
        result = '\n'.join(result)
        return result

    ### PUBLIC PROPERTIES ###

    @property
    def context_name(self):
        return self._context_name

    @property
    def file_name(self):
        return self._file_name

    @property
    def initialization(self):
        return self._initialization

    @property
    def routers(self):
        return self._routers
