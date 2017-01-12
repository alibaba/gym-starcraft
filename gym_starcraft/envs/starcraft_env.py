import numpy as np

import gym
from gym import spaces

from torchcraft_py import torchcraft
from torchcraft_py import proto

import gym_starcraft.utils as utils

DEBUG = 0
SPEED = 0
FRAME_SKIP = 0
DISTANCE_FACTOR = 16


class StarCraftEnv(gym.Env):
    def __init__(self, server_ip, server_port, nb_max_episode_steps):
        self.client = torchcraft.Client(server_ip, server_port)
        self.nb_max_episode_steps = nb_max_episode_steps
        self.nb_steps = 0
        self.nb_episodes = 0
        self.nb_won = 0

        # TODO: adapt to non-1v1 scenarios

        # attack or move, move_degree, move_distance
        action_low = [-1.0, -1.0, -1.0]
        action_high = [1.0, 1.0, 1.0]
        self.action_space = spaces.Box(np.array(action_low),
                                       np.array(action_high))

        # hit points, cooldown, ground range, is enemy, degree, distance (myself)
        # hit points, cooldown, ground range, is enemy (enemy)
        obs_low = [0.0, 0.0, 0.0, 0.0, -1.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        obs_high = [100.0, 100.0, 1.0, 1.0, 1.0, 50.0, 100.0, 100.0, 1.0, 1.0]
        self.observation_space = spaces.Box(np.array(obs_low),
                                            np.array(obs_high))

    def __del__(self):
        self.client.close()

    def _step(self, action):
        self.nb_steps += 1

        self._send_action(action)
        obs = self._recv_observation()
        reward = self._get_reward(obs)
        done = self._get_status()

        return obs, reward, done, {
            'battle_won': bool(self.client.state.d['battle_won'])}

    def _send_action(self, action):
        state = self.client.state.d
        if state is None:
            return self.client.send([])

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
        if action[0] > 0:
            # Attack action
            if myself is None or enemy is None:
                return self.client.send([])
            # TODO: compute the enemy id based on its position
            cmds.append(proto.concat_cmd(
                proto.commands['command_unit_protected'], myself_id,
                proto.unit_command_types['Attack_Unit'], enemy_id))
        else:
            # Move action
            if myself is None or enemy is None:
                self.client.send([])
                return
            degree = action[1] * 180
            distance = (action[2] + 1) * DISTANCE_FACTOR
            x2, y2 = utils.get_position(degree, distance, myself.x, -myself.y)
            cmds.append(proto.concat_cmd(
                proto.commands['command_unit_protected'], myself_id,
                proto.unit_command_types['Move'], -1, x2, -y2))

        return self.client.send(cmds)

    def _recv_observation(self):
        self.client.receive()
        return self._make_observation()

    def _make_observation(self):
        state = self.client.state.d

        myself = None
        enemy = None
        for uid, ut in state['units_myself'].iteritems():
            myself = ut
        for uid, ut in state['units_enemy'].iteritems():
            enemy = ut

        obs = np.zeros(self.observation_space.shape)

        if myself is not None and enemy is not None:
            obs[0] = myself.health
            obs[1] = myself.groundCD
            obs[2] = myself.groundRange / DISTANCE_FACTOR - 1
            obs[3] = 0.0
            obs[4] = utils.get_degree(myself.x, -myself.y, enemy.x,
                                      -enemy.y) / 180
            obs[5] = utils.get_distance(myself.x, -myself.y, enemy.x,
                                        -enemy.y) / DISTANCE_FACTOR - 1
            obs[6] = enemy.health
            obs[7] = enemy.groundCD
            obs[8] = enemy.groundRange / DISTANCE_FACTOR - 1
            obs[9] = 1.0
        else:
            obs[9] = 1.0

        return obs

    def _get_reward(self, obs):
        reward = 0
        if obs[5] + 1 > 1.5:
            reward = -1
        if self.obs_pre[6] > obs[6]:
            reward = 15
        if self.obs_pre[0] > obs[0]:
            reward = -10
        if self._done() and not bool(self.client.state.d['battle_won']):
            reward = -500
        if self._done() and bool(self.client.state.d['battle_won']):
            reward = 1000
            self.nb_won += 1
        if self.nb_steps == self.nb_max_episode_steps:
            reward = -500
        self.obs_pre = obs
        return reward

    def _get_status(self):
        return self._done()

    def _reset(self):
        utils.print_progress(self.nb_episodes, self.nb_won, self.nb_steps)

        if self.nb_steps == self.nb_max_episode_steps:
            self.client.send([proto.concat_cmd(proto.commands['restart'])])
            self.client.receive()
            while not bool(self.client.state.d['game_ended']):
                self.client.send([])
                self.client.receive()

        self.nb_steps = 0
        self.nb_episodes += 1

        self.client.close()
        self.client.connect()
        setup = [proto.concat_cmd(proto.commands['set_speed'], SPEED),
                 proto.concat_cmd(proto.commands['set_gui'], 1),
                 proto.concat_cmd(proto.commands['set_frameskip'], FRAME_SKIP),
                 proto.concat_cmd(proto.commands['set_cmd_optim'], 1)]
        self.client.send(setup)
        self.client.receive()

        obs = self._make_observation()
        self.obs_pre = obs
        return obs

    def _done(self):
        return bool(self.client.state.d['game_ended']) \
               or self.client.state.d['battle_just_ended']

    def render(self, mode='human', close=False):
        pass
