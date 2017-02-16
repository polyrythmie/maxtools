# -*- coding: utf-8 -*-
from abjad import attach
from abjad.tools.abctools.AbjadObject import AbjadObject
from abjad.tools import durationtools
from abjad.tools import selectortools
from abjad.tools import scoretools
import itertools

class MaxPatcher(AbjadObject):

    ### CLASS VARIABLES ###

    __slots__ = (
        '_context_name',
        '_file_name',
        '_routers',
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
        segment_maker,
        ):
        score = segment_maker._score
        segment_metadata = segment_maker._segment_metadata
        previous_segment_metadata = segment_maker._previous_segment_metadata
        assert self.context_name in score
        context = score[self.context_name]
        cue_commands_by_start_offset = self._collect_cue_commands_by_start_offset(context)
        meters_as_timespans = segment_maker.meters_to_timespans(segment_maker._meters)
        cue_command_voice = self._make_cue_command_voice(meters_as_timespans, cue_commands_by_start_offset)
        cues = self._make_cues(cue_command_voice)


    ### PRIVATE METHODS ###

    def _collect_cue_commands_by_start_offset(
        self,
        context,
        ):
        result = {}
        for router in self.routers:
            for start_offset, commands in router._collect_cue_commands_by_start_offset(context).iteritems():
                if not start_offset in result:
                    result[start_offset] = []
                result[start_offset].extend(commands)
        return result

    def _make_cues(
        self,
        cue_command_voice,
        ):
        # TODO
        make_cue_at = []
        for index, measure in enumerate(cue_file):
            for subindex, leaf in enumerate(measure):
                if not all([x.automatic for x in inspect_(leaf).get_indicators(prototype=CueCommand)]):
                    make_cue_at.append([index, subindex])
        if not make_cue_at:
            return
        current_cue_number = 1
        cues = []
        for index, indices in enumerate(make_cue_at):
            if index > 0:
                cues[-1]
            attach(Cue(number=current_cue_number), cue_command_voice[indices[0]][indices[1]])
            current_cue_number += 1


    def _make_cue_command_voice(
        self,
        timespans,
        cue_commands_by_start_offset,
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
                offsets_in_timespan = sorted([start_offset for start_offset in cue_commands_by_start_offset if timespan_start_offset <= start_offset < timespan_stop_offset])
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
                        for cue_command in cue_commands_by_start_offset[offset]:
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
        cue_command_voice = scoretools.Voice(measures)
        return cue_command_voice

    ### PUBLIC PROPERTIES ###

    @property
    def context_name(self):
        return self._context_name

    @property
    def file_name(self):
        return self._file_name

    @property
    def routers(self):
        return self._routers
