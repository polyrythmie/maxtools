# -*- coding: utf-8 -*-
from maxtools.tools.cuetools import CueItem

class AudioConnect(CueItem):

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
        CueItem.__init__(
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

    ### PRIVATE PROPERTIES ###

    @property
    def _arguments(self):
        arguments = [self.inlet, self.outlet, str(self.gain), str(self.ramp)]
        return arguments

    ### PUBLIC PROPERTIES ###

    @property
    def inlet(self):
        return self._inlet

    @property
    def outlet(self):
        return self._outlet

    @property
    def gain(self):
        return self._gain

    @property
    def ramp(self):
        return self._ramp
