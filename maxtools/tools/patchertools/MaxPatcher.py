# -*- coding: utf-8 -*-
from abjad import attach
from abjad import inspect_
from abjad.tools.abctools.AbjadObject import AbjadObject
from abjad.tools import datastructuretools
from abjad.tools import durationtools
from abjad.tools import selectortools
from abjad.tools import scoretools
from abjad.tools import systemtools
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
        ):
        self._file_name = file_name
        self._context_name = context_name
        if not isinstance(routers, (list, tuple)):
            routers = (routers,)
        self._routers = routers

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

        last_patcher_metadata = self._get_last_patcher_metadata()
        last_cue_number = last_patcher_metadata['last_cue_number']
        last_cue_duration_in_ms = last_patcher_metadata['last_cue_duration_in_ms']
        last_effective_settings = last_patcher_metadata['last_effective_settings']
        initialize = (last_cue_number == 0)

        with systemtools.Timer(
            '    total:',
            'Collecting command points:',
            verbose=True,
            ):
            self._command_point_map = self._collect_cue_command_points(
                self._context,
                self.routers,
                initialize=initialize,
                last_effective_settings=last_effective_settings
                )
        with systemtools.Timer(
            '    total:',
            'Creating Cue Voice:',
            verbose=True,
            ):
            self._cue_voice = self._make_cue_voice(meters_as_timespans, self._command_point_map)
            self._cue_voice.name = '{} Cue Voice'.format(self.file_name)
            self._cue_voice.context_name = 'CueVoice'
            self._insert_cue_voice()
        with systemtools.Timer(
            '    total:',
            'Attaching Cues:',
            verbose=True,
            ):
            self._cues = self._attach_cues(
                self._cue_voice,
                last_cue_number,
                last_cue_duration_in_ms)

        self._update_segment_metadata()

        return self._cue_file, self._segment_metadata

    ### PRIVATE METHODS ###

    @staticmethod
    def _collect_cue_command_points(
        context,
        routers,
        initialize=False,
        last_effective_settings=set(),
        ):
        result = {}
        for router in routers:
            cue_command_point_map = router.__call__(context, initialize=initialize, last_effective_settings=last_effective_settings)
            for start_offset, commands in cue_command_point_map.iteritems():
                if not start_offset in result:
                    result[start_offset] = set()
                result[start_offset] |= commands
        return result

    @staticmethod
    def _attach_cues(
        cue_voice,
        last_cue_number=0,
        last_cue_duration_in_ms=0,
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
                reminder_cue = Cue(number=last_cue_number, reminder=True, time_offset=last_cue_duration_in_ms)
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

    def _insert_cue_voice(self):
        cue_staff_name = '{} Cue Staff'.format(self.file_name)
        if not cue_staff_name in self._context:
            self._context.insert(0, scoretools.Staff(name=cue_staff_name, context_name='CueStaff'))
        self._context[cue_staff_name].insert(0, self._cue_voice)

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

        with systemtools.Timer(
            '       total:',
            '   populating measures:',
            verbose=True,
            ):
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
                        container = scoretools.Container([skip])
                        measures.append(container)
                    else:
                        measure = scoretools.Measure(time_signature=time_signature, music=container)
                        measures.append(measure)
        cue_voice = scoretools.Voice(measures)
        return cue_voice

    def _get_last_patcher_metadata(self):
        import importlib
        last_patcher_metadata = self._previous_segment_metadata.get(
            'patcher_metadata',
            collections.OrderedDict(),
            ).get(
                self.file_name,
                {
                    'last_cue_number': 0,
                    'last_cue_duration_in_ms': 0,
                    'last_effective_settings': {},
                    }
                )
        last_effective_settings = set()
        for module, instances in last_patcher_metadata['last_effective_settings'].iteritems():
            module = importlib.import_module(module)
            instances = set([instance[0](*instance[1]) for instance in instances])
            last_effective_settings |= instances
        last_patcher_metadata['last_effective_settings'] = last_effective_settings
        return last_patcher_metadata

    def _format_last_effective_settings_metadata(self):
        last_effective_settings_package_map = {}
        for router in self.routers:
            for setting in router._last_effective_settings:
                settings = setting.__getnewargs__()
                module = setting.__module__
                name = type(setting).__name__
                if not module in last_effective_settings_package_map:
                    last_effective_settings_package_map[module] = []
                last_effective_settings_package_map[module].append([name, settings])
        return last_effective_settings_package_map

    def _update_segment_metadata(self):
        if not self._segment_metadata.get('patcher_metadata', {}):
            self._segment_metadata.update(patcher_metadata=datastructuretools.TypedOrderedDict())
        patcher_metadata = self._segment_metadata.get('patcher_metadata')
        if self._cues:
            last_cue_number = self._cues[-1].number
            last_cue_duration_in_ms = self._cues[-1]._duration_in_ms
        else:
            last_patcher_metadata = self._get_last_patcher_metadata()
            last_cue_number = last_patcher_metadata['last_cue_number']
            last_cue_duration_in_ms = last_patcher_metadata['last_cue_duration_in_ms']
        last_effective_settings = self._format_last_effective_settings_metadata()
        new_metadata = {
            'last_cue_number': last_cue_number,
            'last_cue_duration_in_ms': last_cue_duration_in_ms,
            'last_effective_settings': last_effective_settings,
            }
        patcher_metadata.update({self._file_name: new_metadata})

    ### PRIVATE PROPERTIES ###

    @property
    def _cue_file(self):
        if not self._cues:
            return None
        result = []
        if self._cues[0].number == 1:
            init_commands = set()
            for router in self._routers:
                init_commands |= router._initialization_cue_commands
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
