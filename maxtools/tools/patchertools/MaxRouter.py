# -*- coding: utf-8 -*-
from abjad import inspect_
from abjad import iterate
from abjad.tools.abctools.AbjadObject import AbjadObject
from maxtools.tools.cuetools import CueItem

class MaxRouter(AbjadObject):

    ### CLASS VARIABLES ###

    __slots__ = (
        '_accepts_commands',
        '_route',
        )

    ### INITIALIZER ###

    def __init__(
        self,
        route,
        accepts_commands = None,
        ):
        self._route = route
        if not isinstance(accepts_commands, (list, tuple)):
            accepts_commands = (accepts_commands,)
        self._accepts_commands = accepts_commands

    ### SPECIAL METHODS ###

    def __call__(
        self,
        context,
        ):
        cue_items_by_start_offset = {}
        start_offsets_in_milliseconds = {}
        prototype = self.accepts_commands
        print(prototype)
        for leaf in iterate(context).by_timeline():
            cue_items = [indicator for indicator in inspect_(leaf).get_indicators(prototype=CueItem, unwrap=True) if isinstance(indicator, prototype)]
            if not cue_items:
                continue
            start_offset = inspect_(leaf).get_timespan().start_offset
            start_offset_in_milliseconds = int(inspect_(leaf).get_timespan(in_seconds=True).start_offset * 1000)
            if start_offset in cue_items_by_start_offset:
                cue_items_by_start_offset[start_offset].extend(cue_items)
            else:
                cue_items_by_start_offset[start_offset] = cue_items
            if not start_offset in start_offsets_in_milliseconds:
                start_offsets_in_milliseconds[start_offset] = start_offset_in_milliseconds
        return cue_items_by_start_offset, start_offsets_in_milliseconds

    ### PRIVATE METHODS ###

    ### PRIVATE PROPERTIES ###

    ### PUBLIC METHODS ###

    ### PUBLIC PROPERTIES ###

    @property
    def accepts_commands(self):
        return self._accepts_commands

    @property
    def route(self):
        return self._route
