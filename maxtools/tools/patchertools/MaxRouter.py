# -*- coding: utf-8 -*-
from abjad import inspect_
from abjad import iterate
from abjad.tools.abctools.AbjadObject import AbjadObject
from maxtools.tools.cuetools import CueCommand
from maxtools.tools.patchertools.MaxEvent import MaxEvent
from maxtools.tools.patchertools.MaxSetting import MaxSetting

class MaxRouter(AbjadObject):

    ### CLASS VARIABLES ###

    __slots__ = (
        '_accepts_commands',
        '_initialization',
        '_last_effective_settings',
        '_route',
        )

    ### INITIALIZER ###

    def __init__(
        self,
        route,
        accepts_commands=None,
        initialization=[]
        ):
        self._route = route
        if not isinstance(accepts_commands, (list, tuple)):
            accepts_commands = (accepts_commands,)
        self._accepts_commands = accepts_commands
        if not isinstance(initialization, (list, tuple)):
            initialization = (initialization,)
        for init_command in initialization:
            assert isinstance(init_command, accepts_commands)
        self._initialization = initialization

    ### PRIVATE METHODS ###

    def _collect_command_points(
        self,
        context,
        persisting_settings=set(),
        ):
        command_point_map = {}
        prototype = self.accepts_commands
        for leaf in iterate(context).by_timeline():
            accepted_commands = set([indicator for indicator in inspect_(leaf).get_indicators(prototype=prototype, unwrap=True)])
            if not accepted_commands:
                continue
            start_offset = inspect_(leaf).get_timespan().start_offset
            if start_offset not in command_point_map:
                command_point_map[start_offset] = set()
            command_point_map[start_offset] |= accepted_commands
        command_point_map, self._last_effective_settings = self.remove_redundant_settings(command_point_map, persisting_settings=persisting_settings)
        command_point_map = self._postprocess_commands(command_point_map)
        return command_point_map

    def _postprocess_commands(
        self,
        command_point_map,
        ):
        for start_offset, commands in command_point_map.iteritems():
            command_point_map[start_offset] = set([CueCommand(route=self.route, command=_.command, arguments=_.arguments, automatic=_.automatic) for _ in commands])
        return command_point_map

    ### PRIVATE PROPERTIES ###

    def _get_initialization_commands(self):
        cue_commands = set([CueCommand(route=self.route, command=_.command, arguments=_.arguments, automatic=_.automatic) for _ in self._initialization])
        return cue_commands

    ### PUBLIC METHODS ###

    @staticmethod
    def remove_redundant_settings(
        command_point_map,
        persisting_settings=set(),
        ):
        if not isinstance(persisting_settings, set):
            persisting_settings = set(persisting_settings)
        for start_offset in sorted(command_point_map):
            commands = command_point_map[start_offset]
            new_settings = set([x for x in commands if (isinstance(x, MaxSetting) and not any([x.equivalent_to_setting(y) for y in persisting_settings]))])
            command_point_map[start_offset] = new_settings | set([x for x in commands if (isinstance(x, MaxEvent))])
            persisting_settings = set([x for x in persisting_settings if not any([y.overrides_setting(x) for y in new_settings])]) | new_settings
        return command_point_map, persisting_settings

    ### PUBLIC PROPERTIES ###

    @property
    def accepts_commands(self):
        return self._accepts_commands

    @property
    def route(self):
        return self._route
