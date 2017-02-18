# -*- coding: utf-8 -*-
from abjad.tools.abctools import AbjadObject

class MaxSetting(AbjadObject):
    '''A max setting.
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

    def __eq__(
        self,
        setting,
        ):
        return (
            isinstance(setting, type(self)) and
            self.command == setting.command and
            self.arguments == setting.arguments and
            self.automatic == setting.automatic
            )

    def __hash__(
        self,
        ):
        from abjad.tools import systemtools
        hash_values = systemtools.StorageFormatAgent(self).get_hash_values()
        return hash(hash_values)

    ### PRIVATE PROPERTIES ###

    def _overrides_setting(self, setting):
        return False

    ### PRIVATE METHODS ###

    ### PUBLIC METHODS ###

    def overrides_setting(self, setting):
        return self._overrides_setting

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
