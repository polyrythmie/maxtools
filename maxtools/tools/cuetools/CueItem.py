# -*- coding: utf-8 -*-
from abjad.tools.abctools import AbjadObject
from abjad.tools import durationtools

class CueItem(AbjadObject):
    '''A cue item.
    '''

    __slots__ = (
        '_automatic',
        '_command',
        )

    ### INITIALIZER ###

    def __init__(
        self,
        command,
        automatic=False,
        ):
        self._command = command
        self._automatic = bool(automatic)

    ### SPECIAL METHODS ###

    ### PRIVATE PROPERTIES ###

    @property
    def _arguments(self):
        return []

    @property
    def _cue_item_format(self):
        cue_item_format = [self.command]
        cue_item_format.extend(self._arguments)
        cue_item_format = ' '.join(cue_item_format)
        return cue_item_format

    ### PRIVATE METHODS ###

    ### PUBLIC PROPERTIES ###

    @property
    def automatic(self):
        return self._automatic

    @property
    def command(self):
        return self._command
