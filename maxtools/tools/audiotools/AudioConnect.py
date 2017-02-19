# -*- coding: utf-8 -*-
from maxtools.tools.patchertools.MaxSetting import MaxSetting

class AudioConnect(MaxSetting):

    ### CLASS VARIABLES ###

    __slots__ = (
        '_inlet',
        '_outlet',
        '_gain',
        '_ramp',
        )

    ### INITIALIZER ###

    def __init__(
        self,
        inlet,
        outlet,
        gain,
        ramp=0,
        automatic=False,
        ):
        MaxSetting.__init__(
            self,
            command='connect',
            automatic=automatic,
            )
        self._inlet = inlet
        self._outlet = outlet
        assert 0 <= gain <= 1
        self._gain = gain
        assert 0 <= ramp
        self._ramp = ramp

    ### SPECIAL METHODS ###

    def __format__(self, format_specification=''):
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

    ### PRIVATE PROPERTIES ###

    def _equivalent_to_setting(self, setting):
        return (
            isinstance(setting, type(self)) and
            self.inlet == setting.inlet and
            self.outlet == setting.outlet and
            self.gain == setting.gain
            )

    def _overrides_setting(self, setting):
        return (
            isinstance(setting, type(self)) and
            self.inlet == setting.inlet and
            self.outlet == setting.outlet and
            self.gain != setting.gain
            )

    ### PUBLIC PROPERTIES ###

    @property
    def arguments(self):
        return [self.inlet, self.outlet, self.gain, self.ramp]

    @property
    def gain(self):
        return self._gain

    @property
    def inlet(self):
        return self._inlet

    @property
    def outlet(self):
        return self._outlet

    @property
    def ramp(self):
        return self._ramp
