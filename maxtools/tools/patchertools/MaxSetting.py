# -*- coding: utf-8 -*-
from abjad.tools.abctools import AbjadObject

class MaxSetting(AbjadObject):
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

    ### PRIVATE METHODS ###

    ### PUBLIC PROPERTIES ###

    @property
    def arguments(self):
        return None

    @property
    def automatic(self):
        return self._automatic

    @property
    def command(self):
        return self._command
