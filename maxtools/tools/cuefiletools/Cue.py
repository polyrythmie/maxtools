# -*- coding: utf-8 -*-
from abjad.tools.abctools import AbjadObject
from operator import attrgetter
from abjad.tools import systemtools
from abjad.tools import durationtools

# Make a fancy notehead for cues!
class Cue(AbjadObject):
    '''A cue
    '''

    ### CLASS VARIABLES ###

    __slots__ = (
        '_number',
        '_items',
        '_spanners',
        '_time_offset',
        '_start_offset',
        )

    ### INITIALIZER ###

    def __init__(self, number=None, time_offset=0, start_offset=None):
        if number is not None:
            assert isinstance(number, int), repr(number)
        self._number = number
        self._items = []
        self._spanners = []
        self._time_offset = time_offset
        if not start_offset:
            start_offset = durationtools.Offset(0)
        self._start_offset = start_offset

    ### SPECIAL METHODS ###

    def __format__(self, format_specification=''):
        from abjad.tools import systemtools
        if format_specification in ('', 'cue_file'):
            return self._cue_file_format
        elif format_specification == 'storage':
            return systemtools.StorageFormatAgent(self).get_storage_format()
        return str(self)

    def __getitem__(self, number):
        for cue in self.cues:
            if getattr(cue, 'number', None) == number:
                return item
        raise KeyError

    ### PRIVATE METHODS ###

    def _get_lilypond_format_bundle(self, component=None):
        lilypond_format_bundle = systemtools.LilyPondFormatBundle()
        lilypond_format_bundle.opening.commands.append(self._lilypond_format)
        return lilypond_format_bundle

    ### PRIVATE PROPERTIES ###

    @property
    def _all_cue_items(self):
        cue_items = self.items
        if self.spanners:
            for spanner in self.spanners:
                cue_items.extend(spanner._all_cue_items)
        return cue_items

    @property
    def _cue_file_format(self):
        result = []
        if self.number != 0:
            result.append('------------------------ {}'.format(str(self.number)))
        for item in sorted(self._all_cue_items, key=attrgetter('time_offset', 'route', 'command')):
            result.append(item._get_cue_item_format(cue_time_offset=self.time_offset))
        return '\n'.join(result)

    @property
    def _lilypond_format(self):
        if self.number is not None:
            result = r'\mark #{}'.format(self.number)
            return result
        return r'^\mark'

    ### PUBLIC METHODS ###

    def get_length_in_milliseconds(self):
        length = 0
        last_ramp_end = 0
        for item in self.items:
            if hasattr(item, 'ramp'):
                ramp_end = item.time_offset + item.ramp
                last_ramp_end = last_ramp_end if last_ramp_end > ramp_end else ramp_end
            length += item.time_offset
        return length if length > last_ramp_end else last_ramp_end

    ### PUBLIC PROPERTIES ###

    @property
    def items(self):
        return self._items

    @property
    def number(self):
        return self._number

    @property
    def spanners(self):
        return self._spanners

    @property
    def time_offset(self):
        return self._time_offset

    @property
    def start_offset(self):
        return self._start_offset
