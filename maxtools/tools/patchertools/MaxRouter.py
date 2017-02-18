# -*- coding: utf-8 -*-
from abjad import inspect_
from abjad import iterate
from abjad.tools.abctools.AbjadObject import AbjadObject
from maxtools.tools.cuetools import CueCommand
from maxtools.tools.patchertools.MaxSetting import MaxSetting

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
            if start_offset not in command_point_map:
                command_point_map[start_offset] = []
            command_point_map[start_offset].extend(accepted_commands)
        print("Command point map:")
        for start_offset in sorted(command_point_map):
            print("\t{}: {}".format(start_offset, command_point_map[start_offset]))
        command_point_map = self.remove_redundant_settings(command_point_map)
        command_point_map = self.postprocess_commands(command_point_map)
        return command_point_map

    ### PUBLIC METHODS ###

    @staticmethod
    def remove_redundant_settings(command_point_map):
        # This will break events
        persisting_settings = []
        for start_offset in sorted(command_point_map):
            commands = command_point_map[start_offset]
            new_settings = [x for x in commands if (isinstance(x, MaxSetting) and not any([x == y for y in persisting_settings]))]
            print("New settings: {}".format(new_settings))
            if new_settings:
                persisting_settings = [x for x in persisting_settings if not any([y.overrides_setting(x) for y in new_settings])]
                persisting_settings.extend(new_settings)
                print("Persisting_settings: {}".format(persisting_settings))
            command_point_map[start_offset] = new_settings
        return command_point_map

    def postprocess_commands(self, command_point_map):
        for start_offset, commands in command_point_map.iteritems():
            cue_commands = [CueCommand(route=self.route, command=_.command, arguments=_.arguments, automatic=_.automatic) for _ in commands]
            command_point_map[start_offset] = cue_commands
        return command_point_map

    ### PUBLIC PROPERTIES ###

    @property
    def accepts_commands(self):
        return self._accepts_commands

    @property
    def route(self):
        return self._route
