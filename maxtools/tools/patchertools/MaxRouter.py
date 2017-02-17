# -*- coding: utf-8 -*-
from abjad import inspect_
from abjad import iterate
from abjad.tools.abctools.AbjadObject import AbjadObject
from maxtools.tools.cuetools import CueCommand

class MaxRouter(AbjadObject):

    ### CLASS VARIABLES ###

    __slots__ = (
        '_accepts_commands',
        '_route',
        )

    ### INITIALIZER ###

    def __init__(
        self,
        route,
        accepts_commands = None,
        ):
        self._route = route
        if not isinstance(accepts_commands, (list, tuple)):
            accepts_commands = (accepts_commands,)
        self._accepts_commands = accepts_commands

    ### PRIVATE METHODS ###

    def _collect_command_points(
        self,
        context,
        ):
        command_point_map = {}
        prototype = self.accepts_commands
        for leaf in iterate(context).by_timeline():
            accepted_commands = [indicator for indicator in inspect_(leaf).get_indicators(prototype=prototype, unwrap=True)]
            if not accepted_commands:
                continue
            start_offset = inspect_(leaf).get_timespan().start_offset
            cue_commands = [CueCommand(route=self.route, command=_.command, arguments=_.arguments, automatic=_.automatic) for _ in accepted_commands]
            if start_offset not in command_point_map:
                command_point_map[start_offset] = []
            command_point_map[start_offset].extend(cue_commands)
        return command_point_map

    ### PUBLIC PROPERTIES ###

    @property
    def accepts_commands(self):
        return self._accepts_commands

    @property
    def route(self):
        return self._route
