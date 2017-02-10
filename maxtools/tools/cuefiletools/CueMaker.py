# -*- coding: utf-8 -*-
from abjad import attach
from abjad import inspect_
from abjad import iterate
from abjad.tools.abctools import AbjadObject
from abjad.tools import datastructuretools
from abjad.tools import durationtools
from abjad.tools import scoretools
from abjad.tools import selectiontools
from abjad.tools import selectortools
from abjad.tools import systemtools
from consort.tools import SegmentMaker
from maxtools.tools.cuefiletools.Cue import Cue
from maxtools.tools.cuefiletools.CueFile import CueFile
from maxtools.tools.cuefiletools.CueItem import CueItem
from maxtools.tools.cuefiletools.CueSpanner import CueSpanner

class CueMaker(AbjadObject):
    r'''Cue Maker
    '''

    ### CLASS VARIABLES ###

    __slots__ = (
        '_cue_files',
        '_segment_metadata',
        '_previous_segment_metadata',
        '_score',
        '_meters',
        )

    ### INITIALIZER ###

    def __init__(
        self,
        cue_files,
        ):
        if isinstance(cue_files, CueFile):
            cue_files = (cue_files,)
        assert all(isinstance(x, CueFile) for x in cue_files)
        self._cue_files = cue_files

    ### SPECIAL METHODS ###

    def __call__(
        self,
        score,
        meters,
        segment_metadata=None,
        previous_segment_metadata=None,
        ):
        r'''Call cue maker.

        Returns cue files for each staff group with cues.
        '''
        self._score = score
        self._meters = meters
        self._segment_metadata = segment_metadata or datastructuretools.TypedOrderedDict()
        self._previous_segment_metadata = previous_segment_metadata or datastructuretools.TypedOrderedDict()
        for cue_file in self._cue_files:
            self._process_cue_file(cue_file)
            self._attach_cues(cue_file)
        self.update_segment_metadata()
        return self._cue_files, self._segment_metadata

    ### PRIVATE METHODS ###

    def _process_cue_file(
        self,
        cue_file,
        ):
        with systemtools.Timer(
                enter_message='    Processing cue file ' + cue_file.file_name + ':',
                exit_message='        total:',
                verbose=True,
                ):
                cue_file._cues = self._populate_cues(cue_file.context)

    def _populate_cues(self, context):
        # Needs to attach the cues to time points in context.
        # Does this extremely poorly, need to think about how this will happen.
        with systemtools.Timer(
                enter_message='        Populating cues:',
                exit_message='            total:',
                verbose=True,
                ):
                all_cue_items = self._collect_cue_items(context)
                cue_items_by_time_offset = self._sort_cue_items_by_time_offset(cue_items=all_cue_items)
                last_cue_number, last_cue_time_to_segment_end = self._get_last_cue_by_context_metadata(context=context)
                cues = []
                for time_offset in sorted(cue_items_by_time_offset):
                    cue_items = cue_items_by_time_offset[time_offset]
                    if not all(x.automatic for x in cue_items):
                        cues.append(Cue(number=last_cue_number + 1, time_offset=time_offset, start_offset=cue_items[0].start_offset))
                        last_cue_number += 1
                    if not cues:
                        cues.append(Cue(number=last_cue_number, time_offset=(-1 * last_cue_time_to_segment_end), start_offset=None))
                    print(cues[-1].start_offset)
                    print(time_offset)
                    cues[-1].items.extend(cue_items)
        return cues

    def _attach_cues(
        self,
        cue_file,
        ):
        with systemtools.Timer(
                enter_message='    Processing cue file ' + cue_file.file_name + ':',
                exit_message='        total:',
                verbose=True,
                ):
            cue_staff_name = '{} Cue Staff'.format(cue_file.file_name)
            cue_voice_name = '{} Cue Voice'.format(cue_file.file_name)
            if cue_voice_name not in self._score[cue_file.context]:
                print("Creating {} Cue Staff".format(cue_file.file_name))
                cue_voice = scoretools.Voice(name=cue_voice_name, context_name='CueVoice')
                if cue_staff_name not in self._score[cue_file.context]:
                    cue_staff = scoretools.Staff(name=cue_staff_name, context_name='CueStaff')
                    self._score[cue_file.context].insert(0, cue_staff)
                cue_staff = self._score[cue_staff_name]
                cue_staff.append(cue_voice)
            cue_voice = self._score[cue_voice_name]
            cues = cue_file.cues
            # I don't want to need consort though.
            time_signatures = [_.implied_time_signature for _ in self._meters]
            print("{} Time Signatures".format(len(time_signatures)))
            meters_to_timespans = SegmentMaker.meters_to_timespans(self._meters)
            print("{} Timespans".format(len(meters_to_timespans)))
            measures = []
            for time_signature, timespan in zip(time_signatures, meters_to_timespans):
                result = []
                timespan_start_offset, timespan_stop_offset = timespan.offsets
                for cue in cues:
                    if timespan_start_offset <= cue.start_offset < timespan_stop_offset:
                        result.append(cue)
                if not result:
                    skip = scoretools.Skip(1)
                    multiplier = durationtools.Multiplier(time_signature)
                    attach(multiplier, skip)
                    measure = scoretools.Container([skip])
                    measures.append(measure)
                else:
                    contents = []
                    if result[0].start_offset > timespan_start_offset:
                        duration = result[0].start_offset - timespan_start_offset
                        multiplier, duration = duration.yield_equivalent_durations()[0]
                        skip = scoretools.Skip(duration)
                        attach(multiplier, skip)
                        contents.append(skip)
                    for index, cue in enumerate(result):
                        if index == (len(result) - 1):
                            duration = timespan_stop_offset - cue.start_offset
                        else:
                            duration = result[index + 1].start_offset - cue.start_offset
                        multiplier, duration = duration.yield_equivalent_durations()[0]
                        note = scoretools.Note(0, duration)
                        attach(multiplier, note)
                        attach(cue, note)
                        contents.append(note)
                    measure = scoretools.Container(contents)
                    measures.append(measure)
            cue_voice.extend(measures)

    def _collect_cue_items(self, context):
        with systemtools.Timer(
                enter_message='            Collecting cue items:',
                exit_message='                total:',
                verbose=True,
                ):
                result = []
                for spanner in selectiontools.Descendants(self._score[context]).get_spanners(prototype=CueSpanner):
                    result.extend(spanner._all_cue_items)
                for leaf in iterate(self._score[context]).by_timeline():
                    cue_items = inspect_(leaf).get_indicators(prototype=CueItem, unwrap=True)
                    if not cue_items:
                        continue
                    print(cue_items) ###
                    start_offset_in_milliseconds = int(float(inspect_(leaf).get_timespan(in_seconds=True).start_offset) * 1000)
                    start_offset = inspect_(leaf).get_timespan().start_offset
                    for cue_item in cue_items:
                        cue_item.time_offset = start_offset_in_milliseconds
                        cue_item.start_offset = start_offset
                    result.extend(cue_items)
        return result

    def _get_last_cue_by_context_metadata(self, context):
        last_cue_by_context = self._previous_segment_metadata.get('last_cue_by_context', {})
        last_cue_metadata = last_cue_by_context.get(context, {})
        if last_cue_metadata:
            last_cue_number = last_cue_metadata[0]
            last_cue_time_to_segment_end = last_cue_metadata[1]
        else:
            last_cue_number = 0
            last_cue_time_to_segment_end = 0
        return last_cue_number, last_cue_time_to_segment_end

    def _sort_cue_items_by_time_offset(self, cue_items):
        cue_items_by_time_offset = {}
        for cue_item in cue_items:
            if cue_item.time_offset in cue_items_by_time_offset:
                cue_items_by_time_offset[cue_item.time_offset].append(cue_item)
            else:
                cue_items_by_time_offset[cue_item.time_offset] = [cue_item]
        return cue_items_by_time_offset

    ### PUBLIC METHODS ###

    def get_last_cues_by_context(self):
        result = datastructuretools.TypedOrderedDict()
        for cue_file in self._cue_files:
            context = cue_file.context
            if len(cue_file.cues) >= 1:
                last_cue = cue_file.cues[-1]
                result[context] = [last_cue.number, 0]
            else:
                previous_metadata = self._previous_segment_metadata.get('last_cue_by_context', {})
                last_cue_metadata = previous_metadata.get(context, {})
                if len(last_cue_metadata) == 2:
                    result[context] = last_cue_metadata
                else:
                    result[context] = [0, 0]
        return result

    def update_segment_metadata(self):
        self._segment_metadata.update(
            last_cue_by_context=self.get_last_cues_by_context(),
            )
