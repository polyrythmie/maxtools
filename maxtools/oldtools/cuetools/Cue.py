# -*- coding: utf-8 -*-
from abjad.tools.abctools import AbjadObject
from operator import attrgetter
from abjad.tools import systemtools
from abjad.tools import durationtools
from abjad.tools import markuptools

# Make a fancy notehead for cues!
class Cue(AbjadObject):
    '''A cue
    '''

    ### CLASS VARIABLES ###

    __slots__ = (
        '_number',
        '_cue_items_by_start_offset',
        '_reminder',
        '_start_offset',
        '_start_offsets_in_milliseconds',
        )

    ### INITIALIZER ###

    def __init__(self, number, start_offset=None, reminder=False):
        assert isinstance(number, int), repr(number)
        self._number = number
        if start_offset is None:
            start_offset = durationtools.Offset(0)
        self._start_offset = start_offset
        self._reminder = reminder
        self._cue_items_by_start_offset = {}
        self._start_offsets_in_milliseconds = {}

    ### SPECIAL METHODS ###

    def __format__(self, format_specification=''):
        from abjad.tools import systemtools
        return systemtools.StorageFormatAgent(self).get_storage_format()

    ### PRIVATE METHODS ###

    ### PRIVATE PROPERTIES ###

    @property
    def _cue_file_format(self):
        result = []
        cue_start_offset_in_milliseconds = self.start_offsets_in_milliseconds[self.start_offset]
        if self.number != 0:
            result.append('-------- {}'.format(self.number))
        for start_offset in sorted(self.cue_items_by_start_offset):
            start_offset_in_milliseconds = self.start_offsets_in_milliseconds[start_offset]
            cue_item_time_offset = start_offset_in_milliseconds - cue_start_offset_in_milliseconds
            for cue_item in self.cue_items_by_start_offset[start_offset]:
                result.append('{} {}'.format(cue_item_time_offset, cue_item._cue_item_format))
        return '\n'.join(result)

    ### PUBLIC METHODS ###

    ### PUBLIC PROPERTIES ###

    @property
    def cue_items_by_start_offset(self):
        return self._cue_items_by_start_offset

    @property
    def markup(self):
        markup = markuptools.Markup(self.number)
        return markup

    @property
    def number(self):
        return self._number

    @property
    def reminder(self):
        return self._reminder

    @property
    def start_offset(self):
        return self._start_offset

    @property
    def start_offsets_in_milliseconds(self):
        return self._start_offsets_in_milliseconds
