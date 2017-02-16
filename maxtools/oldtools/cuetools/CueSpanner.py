# -*- coding: utf-8 -*-
from abjad.tools.spannertools.Spanner import Spanner

class CueSpanner(Spanner):

    __slots__ = (
        '_default',
        '_route',
        '_start',
        '_stop',
        )

    ### INITIALIZER ###

    def __init__(
        self,
        route,
        default=None,
        start=None,
        stop=None,
        automatic=(False, False),
        overrides=None,
        ):
        self._route = route
        if default is not None:
            if not isinstance(default, (list, tuple)):
                default = (default,)
        self._default = default

        if start is not None:
            if not isinstance(start, (list, tuple)):
                start = (start,)
        self._start = start

        if stop is not None:
            if not isinstance(stop, (list, tuple)):
                stop = (stop,)
        self._stop = stop

        if not isinstance(automatic, (list, tuple)):
            automatic = (automatic, automatic)
        self._automatic = automatic

        Spanner.__init__(
            self,
            overrides=overrides,
            )

    ### PRIVATE METHODS ###

    def _process_commands(self):
        if self.start is not None:
            attach(self.start, self._music[0])
        if self.default is not None:
            # Run default commands
            pass
        if self.stop is not None:
            attach(self.stop, self._music[-1])

    ### PRIVATE PROPERTIES ###

    ### PUBLIC PROPERTIES ###

    @property
    def automatic(self):
        return self._automatic

    @property
    def default(self):
        return self._default

    @property
    def route(self):
        return self._route

    @property
    def start(self):
        return self._first

    @property
    def stop(self):
        return self._last
