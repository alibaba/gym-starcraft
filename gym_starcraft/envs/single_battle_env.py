import numpy as np

from gym import spaces
from torchcraft_py import proto
import gym_starcraft.utils as utils

import starcraft_env as sc

DISTANCE_FACTOR = 16

class SingleBattleEnv(sc.StarCraftEnv):
    def __init__(self, server_ip, server_port, speed=0, frame_skip=0,
                 self_play=False, max_episode_steps=2000):
        super(SingleBattleEnv, self).__init__(server_ip, server_port, speed,
                                              frame_skip, self_play,
                                              max_episode_steps)

    def _action_space(self):
        # attack or move, move_degree, move_distance
        action_low = [-1.0, -1.0, -1.0]
        action_high = [1.0, 1.0, 1.0]
        return spaces.Box(np.array(action_low), np.array(action_high))

    def _observation_space(self):
        # hit points, cooldown, ground range, is enemy, degree, distance (myself)
        # hit points, cooldown, ground range, is enemy (enemy)
        obs_low = [0.0, 0.0, 0.0, 0.0, -1.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        obs_high = [100.0, 100.0, 1.0, 1.0, 1.0, 50.0, 100.0, 100.0, 1.0, 1.0]
        return spaces.Box(np.array(obs_low), np.array(obs_high))

    def _make_commands(self, action):
        cmds = []
        if self.state is None or not action:
            return cmds

        myself_id = None
        myself = None
        enemy_id = None
        enemy = None
        for uid, ut in self.state['units_myself'].iteritems():
            myself_id = uid
            myself = ut
        for uid, ut in self.state['units_enemy'].iteritems():
            enemy_id = uid
            enemy = ut

        if action[0] > 0:
            # Attack action
            if myself is None or enemy is None:
                return cmds
            # TODO: compute the enemy id based on its position
            cmds.append(proto.concat_cmd(
                proto.commands['command_unit_protected'], myself_id,
                proto.unit_command_types['Attack_Unit'], enemy_id))
        else:
            # Move action
            if myself is None or enemy is None:
                return cmds
            degree = action[1] * 180
            distance = (action[2] + 1) * DISTANCE_FACTOR
            x2, y2 = utils.get_position(degree, distance, myself.x, -myself.y)
            cmds.append(proto.concat_cmd(
                proto.commands['command_unit_protected'], myself_id,
                proto.unit_command_types['Move'], -1, x2, -y2))

        return cmds

    def _make_observation(self):
        myself = None
        enemy = None
        for uid, ut in self.state['units_myself'].iteritems():
            myself = ut
        for uid, ut in self.state['units_enemy'].iteritems():
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

    def _compute_reward(self):
        reward = 0
        if self.obs[5] + 1 > 1.5:
            reward = -1
        if self.obs_pre[6] > self.obs[6]:
            reward = 15
        if self.obs_pre[0] > self.obs[0]:
            reward = -10
        if self._check_done() and not bool(self.state['battle_won']):
            reward = -500
        if self._check_done() and bool(self.state['battle_won']):
            reward = 1000
            self.episode_wins += 1
        if self.episode_steps == self.max_episode_steps:
            reward = -500
        return reward
