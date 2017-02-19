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

    def __format__(self):
        from abjad.tools import systemtools
        agent = systemtools.StorageFormatAgent(self)
        names = list(agent.signature_keyword_names)
        #values = [list(self._collection.items())]
        return systemtools.FormatSpecification(
            self,
            repr_is_indented=False,
            #storage_format_args_values=values,
            storage_format_kwargs_names=names,
            storage_format_includes_root_package=True,
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
