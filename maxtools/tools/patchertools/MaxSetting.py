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
            self.arguments == setting.arguments
            )

    def __hash__(
        self,
        ):
        from abjad.tools import systemtools
        hash_values = systemtools.StorageFormatAgent(self).get_hash_values()
        return hash(hash_values)

    ### PRIVATE PROPERTIES ###

    def _equivalent_to_setting(self, setting):
        return self == setting

    def _get_format_specification(self):
        from abjad.tools import systemtools
        agent = systemtools.StorageFormatAgent(self)
        names = list(agent.signature_keyword_names)
        return systemtools.FormatSpecification(
            client=self,
            storage_format_kwargs_names=names,
            )

    def _overrides_setting(self, setting):
        return False

    ### PRIVATE METHODS ###

    ### PUBLIC METHODS ###

    def equivalent_to_setting(self, setting):
        return self._equivalent_to_setting(setting)

    def overrides_setting(self, setting):
        return self._overrides_setting(setting)

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
