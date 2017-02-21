# -*- coding: utf-8 -*-
from maxtools.tools.patchertools.MaxSetting import MaxSetting

class MidiConnect(MaxSetting):

    ### CLASS VARIABLES ###

    __slots__ = (
        '_inlet',
        '_outlet',
        '_input_range',
        '_output_range',
        '_scaling_exponent',
        )

    ### INITIALIZER ###

    def __init__(
        self,
        inlet,
        outlet,
        input_range=(0, 127),
        output_range=(0, 1),
        scaling_exponent=1,
        automatic=False,
        ):
        MaxSetting.__init__(
            self,
            command='connect',
            automatic=automatic,
            )
        self._inlet = inlet
        self._outlet = outlet
        assert isinstance(input_range, (list, tuple))
        assert isinstance(input_range[0], int) and isinstance(input_range[1], int)
        assert isinstance(output_range, (list, tuple))
        self._input_range = input_range
        self._output_range = output_range
        self._scaling_exponent = scaling_exponent

    ### SPECIAL METHODS ###

    def __getnewargs__(self):
        return (self.inlet, self.outlet, self.input_range, self.output_range, self.scaling_exponent, self.automatic)

    ### PRIVATE PROPERTIES ###

    def _equivalent_to_setting(self, setting):
        return (
            isinstance(setting, type(self)) and
            self.arguments == setting.arguments
            )

    def _overrides_setting(self, setting):
        return (
            isinstance(setting, type(self)) and
            self.inlet == setting.inlet and
            self.outlet == setting.outlet and
            self.arguments != setting.arguments
            )

    ### PUBLIC PROPERTIES ###

    @property
    def arguments(self):
        return [self.inlet, self.input_range[0], self.input_range[1], self.outlet, self.output_range[0], self.output_range[1], self.scaling_exponent]

    @property
    def input_range(self):
        return self._input_range

    @property
    def output_range(self):
        return self._output_range

    @property
    def inlet(self):
        return self._inlet

    @property
    def outlet(self):
        return self._outlet

    @property
    def scaling_exponent(self):
        return self._scaling_exponent
