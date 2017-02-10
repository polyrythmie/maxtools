# -*- coding: utf-8 -*-
from maxtools.tools.cuefiletools import CueItem

class AudioDisconnect(CueItem):
    r'''An Audio disconnect cue item.
    '''

    ### CLASS VARIABLES ###

    __slots__ = (
        '_inlet',
        '_outlet',
        )

    ### INITIALIZER ###

    def __init__(
        self,
        inlet,
        outlet,
        automatic=False,
        time_offset=None,
        start_offset=None,
        ):
        CueItem.__init__(
            self,
            route='audio',
            command='disconnect',
            time_offset=time_offset,
            start_offset=start_offset,
            automatic=automatic,
            )
        self._inlet = inlet
        self._outlet = outlet

    ### SPECIAL METHODS ###

    ### PRIVATE METHODS ###

    def _get_cue_item_format(self, cue_time_offset=0):
        result = [super(AudioDisconnect, self)._get_cue_item_format(cue_time_offset=cue_time_offset)]
        result.append('{} {}'.format(
            self.inlet,
            self.outlet,
            ))
        return ' '.join(result)

    ### PUBLIC PROPERTIES ###

    @property
    def inlet(self):
        return self._inlet

    @property
    def outlet(self):
        return self._outlet
