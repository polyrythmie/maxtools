# -*- coding: utf-8 -*-
from maxtools.tools.cuefiletools import CueItem

# TODO:
### Separate classes for AudioSpanner (which makes audio connection/disconnection items)
### And AudioConnection/AudioDisconnection (which are cue items)

class AudioConnect(CueItem):
    r'''An Audio connect cue item.
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
        time_offset=None,
        start_offset=None,
        ):
        CueItem.__init__(
            self,
            route='audio',
            command='connect',
            time_offset=time_offset,
            start_offset=start_offset,
            automatic=automatic,
            )
        self._inlet = inlet
        self._outlet = outlet
        assert 0 <= gain <= 1
        self._gain = gain
        self._ramp = ramp or 0

    ### SPECIAL METHODS ###

    ### PRIVATE METHODS ###

    def _get_cue_item_format(self, cue_time_offset=0):
        result = [super(AudioConnect, self)._get_cue_item_format(cue_time_offset=cue_time_offset)]
        result.append('{} {} {} {}'.format(
            self.inlet,
            self.outlet,
            self.gain,
            self.ramp
            ))
        return ' '.join(result)

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
