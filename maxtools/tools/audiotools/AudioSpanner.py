# -*- coding: utf-8 -*-
from maxtools.tools.audiotools import AudioConnect
from maxtools.tools.audiotools import AudioDisconnect
from maxtools.tools.cuefiletools import CueSpanner

class AudioSpanner(CueSpanner):
    r'''An Audio cue spanner.
    '''

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
        ramp=None,
        automatic=False,
        ):
        CueSpanner.__init__(
            self,
            automatic=automatic,
            overrides=None,
            )
        self._inlet = inlet
        self._outlet = outlet
        assert 0 <= gain <= 1
        self._gain = gain
        self._ramp = ramp or 0

    ### SPECIAL METHODS ###

    def __getnewargs__(self):
        r'''Gets new arguments of spanner.
        '''
        return (
            self.inlet,
            self.outlet,
            self.gain,
            self.ramp,
            self.automatic,
            )

    ### PRIVATE PROPERTIES ###

    @property
    def _opening_cue_items(self):
        time_offset = int(float(self._get_timespan(in_seconds=True).start_offset * 1000))
        start_offset = self._get_timespan().start_offset
        cue_item = AudioConnect(inlet=self.inlet, outlet=self.outlet, gain=self.gain, ramp=self.ramp, automatic=self.automatic[0], time_offset=time_offset, start_offset=start_offset)
        return [cue_item]

    @property
    def _closing_cue_items(self):
        time_offset = int(float(self._get_timespan(in_seconds=True).stop_offset * 1000))
        stop_offset = self._get_timespan().stop_offset
        cue_item = AudioDisconnect(inlet=self.inlet, outlet=self.outlet, automatic=self.automatic[1], time_offset=time_offset, start_offset=stop_offset)
        return [cue_item]

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
