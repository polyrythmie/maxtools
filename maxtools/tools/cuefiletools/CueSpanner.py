# -*- coding: utf-8 -*-
from abjad.tools.spannertools.Spanner import Spanner
from maxtools.tools.cuefiletools import CueItem

class CueSpanner(Spanner):

    __slots__ = (
        '_route',
        '_command',
        '_automatic',
        )

    ### INITIALIZER ###

    def __init__(
        self,
        automatic=False,
        overrides=None,
        ):
        Spanner.__init__(
            self,
            overrides=overrides,
            )
        if not isinstance(automatic, (list, tuple)):
            automatic = (automatic, automatic)
        assert all(isinstance(x, bool) for x in automatic)
        self._automatic = automatic

    ### PRIVATE PROPERTIES ###

    @property
    def _all_cue_items(self):
        cue_items = self._opening_cue_items
        cue_items.extend(self._closing_cue_items)
        return cue_items

    @property
    def _opening_cue_items(self):
        return None

    @property
    def _closing_cue_items(self):
        return None

    ### PUBLIC PROPERTIES ###

    @property
    def automatic(self):
        return self._automatic
