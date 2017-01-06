import numpy as np

import gym
from gym import spaces

from torchcraft_py import torchcraft
from torchcraft_py import proto

import gym_starcraft.utils as utils

DEBUG = 0
SPEED = 0
FRAME_SKIP = 9


class StarCraftEnv(gym.Env):
    def __init__(self, server_ip):
        self.client = torchcraft.Client(server_ip)

        # attack, move, attack_degree, attack_distance, move_degree, move_distance
        action_low = [-1.0, -1.0, -180.0, 0.0, -180.0, 16.0]
        action_high = [1.0, 1.0, 180.0, 32.0, 180.0, 32.0]
        self.action_space = spaces.Box(np.array(action_low),
                                       np.array(action_high))

        # hit points, shield, cooldown, is enemy, x, y, degree, distance
        obs_low = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -180.0, 0.0]
        obs_high = [100.0, 100.0, 100.0, 1.0, 800.0, 600.0, 180.0, 800.0]
        self.observation_space = spaces.Box(np.array(obs_low),
                                            np.array(obs_high))

    def __del__(self):
        self.client.close()

    def _step(self, action):
        self._send_action(action)
        self._recv_state()

        obs = self._get_observation()
        reward = self._get_reward()
        done = self._get_status()

        return obs, reward, done, {}

    def _send_action(self, action):
        state = self.client.state.d
        if state is None:
            return self.client.send("")

        myself_id = None
        myself = None
        enemy_id = None
        enemy = None
        for uid, ut in state['units_myself'].iteritems():
            myself_id = uid
            myself = ut
        for uid, ut in state['units_enemy'].iteritems():
            enemy_id = uid
            enemy = ut

        cmds = []
        if action[0] > action[1]:
            # Attack action
            if myself is None or enemy is None:
                return self.client.send("")
            degree = action[2]
            distance = action[3]
            # TODO: compute enemy's position
            cmds.append(proto.concat_cmd(
                proto.commands['command_unit_protected'], myself_id,
                proto.unit_command_types['Attack_Unit'], enemy_id))
        else:
            # Move action
            if myself is None or enemy is None:
                self.client.send("")
                return
            degree = action[4]
            distance = action[5]
            x2, y2 = utils.get_position(degree, distance, myself.x, myself.y)
            cmds.append(proto.concat_cmd(
                proto.commands['command_unit_protected'], myself_id,
                proto.unit_command_types['Move'], -1, x2, y2))

        return self.client.send(cmds)

    def _recv_state(self):
        self.client.receive()

    def _get_reward(self):
        if bool(self.client.state.d['battle_won']):
            return 1
        return 0

    def _get_observation(self):
        return self.client.state.d

    def _get_status(self):
        return self._done()

    def _reset(self):
        self.client.close()
        self.client.connect()

        setup = [proto.concat_cmd(proto.commands['set_speed'], SPEED),
                 proto.concat_cmd(proto.commands['set_gui'], 1),
                 proto.concat_cmd(proto.commands['set_frameskip'], FRAME_SKIP),
                 proto.concat_cmd(proto.commands['set_cmd_optim'], 1)]
        self.client.send(setup)

        return self.client.state.d

    def _done(self):
        return bool(self.client.state.d['game_ended']) \
               or self.client.state.d['battle_just_ended'] \
               or self.client.state.d['waiting_for_restart']
