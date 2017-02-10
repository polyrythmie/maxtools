# -*- coding: utf-8 -*-
from abjad.tools.abctools import AbjadObject
from abjad.tools import durationtools

# Make time offset an offset and time_offset_in_milliseconds a property.
# Actually make start_offset an offset and time_offset the cue time in ms.
class CueItem(AbjadObject):
    '''A cue item.
    '''

    __slots__ = (
        '_automatic',
        '_route',
        '_command',
        '_start_offset',
        '_time_offset',
        )

    ### INITIALIZER ###

    def __init__(
        self,
        route,
        command,
        automatic=False,
        start_offset=None,
        time_offset=None,
        ):
        self._route = route
        self._command = command
        self._automatic = bool(automatic)
        if time_offset is None:
            time_offset = 0
        assert isinstance(time_offset, int)
        self._time_offset = int(time_offset)
        if start_offset is not None:
            assert isinstance(start_offset, durationtools.Offset)
        self._start_offset = start_offset

    ### SPECIAL METHODS ###

    ### PRIVATE METHODS ###

    def _get_cue_item_format(self, cue_time_offset=0):
        return '{} {} {}'.format(self.time_offset - cue_time_offset, self.route, self.command)

    ### PUBLIC PROPERTIES ###

    @property
    def automatic(self):
        return self._automatic

    @property
    def route(self):
        return self._route

    @property
    def command(self):
        return self._command

    @property
    def time_offset(self):
        return self._time_offset

    @property
    def start_offset(self):
        return self._start_offset
