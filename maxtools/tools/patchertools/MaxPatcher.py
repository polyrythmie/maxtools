# -*- coding: utf-8 -*-
from abjad.tools.abctools.AbjadObject import AbjadObject
from abjad.tools import systemtools
from maxtools.tools.cuetools import Cue
from maxtools.tools.cuetools import CueVoiceSpanner

class MaxPatcher(AbjadObject):
    r'''A max patcher specification.
    '''

    ### CLASS VARIABLES ###

    __slots__ = (
        '_context_name',
        '_cues',
        '_cue_items_by_start_offset',
        '_file_name',
        '_routers',
        '_meters',
        '_start_offsets_in_milliseconds',
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
        self._cues = []

    ### SPECIAL METHODS ###

    def __call__(self, *args, **kwds):
        import collections
        from abjad.tools import scoretools
        from consort.tools import SegmentMaker
        if len(args) == 1:
            # Needs to check if this is actually a segment maker without importing the whole library.
            segment_maker = args[0]
            score = segment_maker._score
            segment_metadata = segment_maker._segment_metadata
            previous_segment_metadata = segment_maker._previous_segment_metadata
            self._meters = segment_maker._meters
            assert self.context_name in score
            context = score[self.context_name]
            self._collect_cue_items(context)
            self._populate_cues(previous_segment_metadata)
            self._attach_cues_to_context(context)
            return self._cue_file
        else:
            assert 'score' in kwds
            score = kwds['score']
            assert isinstance(score, scoretools.Score) and self.context_name in score
            context = score[self.context_name]
            if 'meters' not in kwds or kwds['meters'] is None:
                meters = self._get_meters_in_context(context)
            else:
                meters = kwds['meters']
            self._meters = meters
            self._collect_cue_items(context)
            if 'previous_segment_metadata' not in kwds:
                previous_segment_metadata = collections.OrderedDict()
            else:
                previous_segment_metadata = kwds['previous_segment_metadata']
            self._populate_cues(previous_segment_metadata)
            self._attach_cues_to_context(context)
            return self._cue_file

    def __format__(self, format_specification=''):
        from abjad.tools import systemtools
        return systemtools.StorageFormatAgent(self).get_storage_format()

    ### PRIVATE METHODS ###

    def _attach_cues_to_context(self, context):
        from abjad import attach
        from abjad.tools import scoretools, durationtools
        import itertools
        cue_voice = self._get_cue_voice(context)
        timespans = self._get_meters_as_timespans()
        iterator = itertools.groupby(timespans, lambda x: x.annotation.implied_time_signature)
        measures = []
        for time_signature, group in iterator:
            containers = []
            for timespan in group:
                timespan_start_offset, timespan_stop_offset = timespan.offsets
                cues_in_timespan = []
                for cue in self._cues:
                    if timespan_start_offset <= cue.start_offset < timespan_stop_offset:
                        cues_in_timespan.append(cue)
                if not cues_in_timespan:
                    containers.append([])
                else:
                    contents = []
                    if cues_in_timespan[0].start_offset > timespan_start_offset:
                        duration = cues_in_timespan[0].start_offset - timespan_start_offset
                        multiplier, duration = duration.yield_equivalent_durations()[0]
                        skip = scoretools.Skip(duration)
                        attach(multiplier, skip)
                        contents.append(skip)
                    for index, cue in enumerate(cues_in_timespan):
                        if index == (len(cues_in_timespan) - 1):
                            duration = timespan_stop_offset - cue.start_offset
                        else:
                            duration = cues_in_timespan[index + 1].start_offset - cue.start_offset
                        multiplier, duration = duration.yield_equivalent_durations()[0]
                        note = scoretools.Note(0, duration)
                        attach(multiplier, note)
                        attach(cue, note)
                        contents.append(note)
                    containers.append(contents)
            subiterator = itertools.groupby(containers, lambda x: x)
            for container, subgroup in subiterator:
                if not container:
                    skip = scoretools.Skip(1)
                    multiplier = durationtools.Multiplier(time_signature) * len(tuple(subgroup))
                    attach(multiplier, skip)
                    measure = scoretools.Container([skip])
                    measures.append(measure)
                else:
                    measure = scoretools.Container(container)
                    measures.append(measure)
        print(measures)
        cue_voice.extend(measures)
        attach(CueVoiceSpanner(), cue_voice[:])

    def _get_meters_as_timespans(self):
        # Should work? Copied from Consort SegmentMaker so as not to require the library.
        from abjad.tools import durationtools, mathtools, timespantools
        durations = [_.duration for _ in self._meters]
        offsets = mathtools.cumulative_sums(durations)
        offsets = [durationtools.Offset(_) for _ in offsets]
        timespans = []
        for i, meter in enumerate(self._meters):
            start_offset = offsets[i]
            stop_offset = offsets[i + 1]
            timespan = timespantools.AnnotatedTimespan(
                annotation=meter,
                start_offset=start_offset,
                stop_offset=stop_offset,
                )
            timespans.append(timespan)
        return timespans

    def _get_meters_in_context(self, context):
        from abjad.tools import selectortools, scoretools, metertools
        meters = []
        selector = selectortools.Selector().by_class(prototype=scoretools.Voice).flatten()
        selection = max(selector(context))
        selector = selectortools.Selector().by_leaf().by_logical_measure()
        selection = selector(selection)
        for select in selection:
            meters.append(metertools.Meter(select.get_duration()))
        return meters

    def _get_cue_voice(self, context):
        from abjad.tools import scoretools
        cue_staff_name = '{} Cue Staff'.format(self.file_name)
        cue_voice_name = '{} Cue Voice'.format(self.file_name)
        if cue_voice_name not in context:
            cue_voice = scoretools.Voice(name=cue_voice_name, context_name='CueVoice')
            if cue_staff_name not in context:
                cue_staff = scoretools.Staff(name=cue_staff_name, context_name='CueStaff')
                context.insert(0, cue_staff)
            cue_staff = context[cue_staff_name]
            cue_staff.append(cue_voice)
        return context[cue_voice_name]

    def _collect_cue_items(self, context):
        all_cue_items_by_start_offset = {}
        all_start_offsets_in_milliseconds = {}
        for router in self.routers:
            cue_items_by_start_offset, start_offsets_in_milliseconds = router.__call__(context)
            for start_offset in cue_items_by_start_offset:
                cue_items = cue_items_by_start_offset[start_offset]
                if start_offset in all_cue_items_by_start_offset:
                    all_cue_items_by_start_offset[start_offset].extend(cue_items)
                else:
                    all_cue_items_by_start_offset[start_offset] = cue_items
            for start_offset in start_offsets_in_milliseconds:
                if start_offset not in all_start_offsets_in_milliseconds:
                    all_start_offsets_in_milliseconds[start_offset] = start_offsets_in_milliseconds[start_offset]
        self._cue_items_by_start_offset = all_cue_items_by_start_offset
        self._start_offsets_in_milliseconds = all_start_offsets_in_milliseconds

    def _populate_cues(self, previous_segment_metadata):
        last_cue_by_context = previous_segment_metadata.get('last_cue_by_context', {})
        last_cue_metadata = last_cue_by_context.get(self.context_name, {})
        if last_cue_metadata:
            last_cue_number = last_cue_metadata[0]
            last_cue_time_to_segment_end = last_cue_metadata[1]
        else:
            last_cue_number = 0
            last_cue_time_to_segment_end = 0
        current_cue_number = last_cue_number
        cues = []
        for start_offset in sorted(self._cue_items_by_start_offset):
            cue_items = self._cue_items_by_start_offset[start_offset]
            start_offset_in_milliseconds = self._start_offsets_in_milliseconds[start_offset]
            if not all(cue_item.automatic for cue_item in cue_items):
                current_cue_number += 1
                cues.append(Cue(number=current_cue_number, start_offset=start_offset))
            if not cues:
                cues.append(Cue(number=current_cue_number, reminder=True))
            if not start_offset in cues[-1].cue_items_by_start_offset:
                cues[-1].cue_items_by_start_offset[start_offset] = []
            cues[-1].cue_items_by_start_offset[start_offset].extend(cue_items)
            cues[-1].start_offsets_in_milliseconds[start_offset] = start_offset_in_milliseconds
        self._cues = cues

    ### PRIVATE PROPERTIES ###

    @property
    def _cue_file(self):
        result = []
        for cue in self._cues:
            result.append(cue._cue_file_format)
        return '\n'.join(result)

    ### PUBLIC METHODS ###

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
