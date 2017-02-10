# -*- coding: utf-8 -*-
from maxtools.tools.cuefiletools import CueItem

class MidiConnection(CueItem):
    r'''A Midi connection cue item.
    '''

    ### CLASS VARIABLES ###

    __slots__ = (
        '_inlet',
        '_inlet_range',
        '_outlet',
        '_outlet_range',
        '_exponent',
        '_scale',
        )

    ### INITIALIZER ###

    def __init__(
        self,
        inlet,
        inlet_range,
        outlet,
        outlet_range,
        exponent=None,
        time_offset=None,
        ):
        self._inlet = inlet
        self._outlet = outlet
        assert isinstance(inlet_range, (list, tuple)) and len(inlet_range) == 2, "Invalid inlet range"
        assert isinstance(inlet_range[0], (int)) and isinstance(inlet_range[1], (int)), "Invalid inlet range, must have int values."
        self._inlet_range = inlet_range
        assert isinstance(outlet_range, (list, tuple)) and len(outlet_range) == 2, "Invalid outlet range"
        assert isinstance(outlet_range[0], (int, float)) and isinstance(outlet_range[1], (int, float))
        self._outlet_range = outlet_range
        if exponent is None:
            exponent = 1
        self._exponent = exponent
        self._scale = '{} {} {} {} {}'.format(inlet_range[0], inlet_range[1], outlet_range[0], outlet_range[1], exponent)
        if time_offset is None:
            time_offset = 0
        CueItem.__init__(
            self,
            route='midi',
            command='connect',
            time_offset=time_offset,
            )

    ### SPECIAL METHODS ###

    ### PRIVATE PROPERTIES ###

    @property
    def _cue_item_format(self):
        result = [super(MidiConnection, self)._cue_item_format]
        result.extend([self.inlet, self.outlet, self._scale])
        result = ' '.join(result)
        return result

    ### PUBLIC PROPERTIES ###

    @property
    def inlet(self):
        return self._inlet

    @property
    def inlet_range(self):
        return self._inlet_range

    @property
    def outlet(self):
        return self._outlet

    @property
    def outlet_range(self):
        return self._outlet_range

    @property
    def exponent(self):
        return self._exponent
