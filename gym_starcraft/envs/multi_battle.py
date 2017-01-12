import numpy as np

from gym import spaces
from torchcraft_py import proto
import gym_starcraft.utils as utils

import starcraft_env as sc

DEBUG = 0
SPEED = 0
FRAME_SKIP = 0
DISTANCE_FACTOR = 16


class MultiBattleEnv(sc.StarCraftEnv):
    def __init__(self, server_ip, server_port, speed=0, frame_skip=0,
                 self_play=False, max_episode_steps=2000, nb_my_units=2,
                 nb_enemy_units=2):
        super(MultiBattleEnv, self).__init__(server_ip, server_port, speed,
                                             frame_skip, self_play,
                                             max_episode_steps)

        self.nb_my_units = nb_my_units
        self.nb_enemy_units = nb_enemy_units

    def _action_space(self):
        # attack or move, move_degree, move_distance
        action_low = np.zeros(self.nb_my_units * (3 + self.nb_enemy_units))
        action_high = np.ones(self.nb_my_units * (3 + self.nb_enemy_units))
        return spaces.Box(action_low, action_high)

    def _observation_space(self):
        # hit points, cooldown, ground range, is enemy, degree, distance (myself)
        # hit points, cooldown, ground range, is enemy (enemy)
        obs_low_myself = [0.0, 0.0, 0.0, 0.0] * self.nb_my_units
        obs_low_enemy = [0.0, 0.0, 0.0, 0.0] * self.nb_enemy_units
        obs_low_rel = [-1.0, 0.0] * (self.nb_enemy_units * self.nb_my_units)
        obs_low = obs_low_myself + obs_low_enemy + obs_low_rel
        obs_high_myself = [100.0, 100.0, 1.0, 1.0] * self.nb_my_units
        obs_high_enemy = [100.0, 100.0, 1.0, 1.0] * self.nb_enemy_units
        obs_high_rel = [1.0, 50.0] * (self.nb_enemy_units * self.nb_my_units)
        obs_high = obs_high_myself + obs_high_enemy + obs_high_rel
        self.observation_space = spaces.Box(np.array(obs_low),
                                            np.array(obs_high))

    def _make_commands(self, action):
        cmds = []
        state = self.client.state.d
        if state is None:
            return cmds

        myself_ids = [None] * self.nb_my_units
        myself = [None] * self.nb_my_units
        enemy_ids = [None] * self.nb_enemy_units
        enemy = [None] * self.nb_enemy_units
        for idx, (uid, ut) in enumerate(state['units_myself'].iteritems()):
            myself_ids[idx] = uid
            myself[idx] = ut
        for idx, (uid, ut) in enumerate(state['units_enemy'].iteritems()):
            enemy_ids[idx] = uid
            enemy[idx] = ut

        dist = np.zeros(self.nb_enemy_units)
        dist.fill(99999999)

        for idx in range(self.nb_my_units):
            if myself[idx] is None:
                return cmds
                # for idx2 in range(self.nb_enemy_units):
                # if enemy[idx2] is not None:
                #   dist[idx2] = utils.get_distance(myself[idx].x, -myself[idx].y, enemy[idx2].x,
                #                                 -enemy[idx2].y) / DISTANCE_FACTOR - 1
            # attack_id = np.argmin(dist)
            # min_dist = np.min(dist)
            attack_idx = np.argmax(action[(3 + self.nb_enemy_units) * idx + 3:(3 + self.nb_enemy_units) * (idx + 1)])
            # print "act:",action
            if action[idx * (3 + self.nb_enemy_units)] > 0 and enemy_ids is not None:  # and min_dist+1 < myself[idx].groundRange / DISTANCE_FACTOR:
                # Attack action
                cmds.append(proto.concat_cmd(
                    proto.commands['command_unit_protected'], myself_ids[idx],
                    # proto.unit_command_types['Attack_Unit'], enemy_ids[attack_id.astype(np.intp)]))
                    proto.unit_command_types['Attack_Unit'],
                    enemy_ids[attack_idx.astype(np.intp)]))
            else:
                # Move action
                degree = action[1 + idx * (3 + self.nb_enemy_units)] * 180
                distance = (action[2 + idx * (3 + self.nb_enemy_units)] + 1) * DISTANCE_FACTOR
                x2, y2 = utils.get_position(degree, distance, myself[idx].x,
                                            -myself[idx].y)
                cmds.append(proto.concat_cmd(
                    proto.commands['command_unit_protected'], myself_ids[idx],
                    proto.unit_command_types['Move'], -1, x2, -y2))
            dist.fill(9999)

        return self.client.send(cmds)

    def _make_observation(self):
        myself = [None] * self.nb_my_units
        enemy = [None] * self.nb_enemy_units
        for idx, (uid, ut) in enumerate(self.state['units_myself'].iteritems()):
            myself[idx] = ut
        for idx, (uid, ut) in enumerate(self.state['units_enemy'].iteritems()):
            enemy[idx] = ut

        obs = np.zeros(self.observation_space.shape)

        for idx in range(self.nb_my_units):
            if myself[idx] is not None:
                obs[0 + 4 * idx] = myself[idx].health
                obs[1 + 4 * idx] = myself[idx].groundCD
                obs[2 + 4 * idx] = myself[idx].groundRange / DISTANCE_FACTOR - 1
                obs[3 + 4 * idx] = 0.0
        for idx in range(self.nb_enemy_units):
            if enemy[idx] is not None:
                obs[4 * self.nb_my_units + 0 + 4 * idx] = enemy[idx].health
                obs[4 * self.nb_my_units + 1 + 4 * idx] = enemy[idx].groundCD
                obs[4 * self.nb_my_units + 2 + 4 * idx] = enemy[idx].groundRange / DISTANCE_FACTOR - 1
                obs[4 * self.nb_my_units + 3 + 4 * idx] = 1.0
        for idx1 in range(self.nb_my_units):
            if myself[idx1] is not None:
                for idx2 in range(self.nb_enemy_units):
                    if enemy[idx2] is not None:
                        obs[4 * (self.nb_enemy_units + self.nb_my_units) + 0 + 2 * (self.nb_enemy_units * idx1 + idx2)] = utils.get_degree(myself[idx1].x, -myself[idx1].y, enemy[idx2].x, -enemy[idx2].y) / 180
                        obs[4 * (self.nb_enemy_units + self.nb_my_units) + 1 + 2 * (self.nb_enemy_units * idx1 + idx2)] = utils.get_distance(myself[idx1].x, -myself[idx1].y, enemy[idx2].x, -enemy[idx2].y) / DISTANCE_FACTOR - 1

        return obs

    def _compute_reward(self):
        reward = 0
        for idx1 in range(self.nb_my_units):
            if self.obs_pre[0 + 4 * idx1] > self.obs[0 + 4 * idx1]:
                reward += 20
            for idx2 in range(self.nb_enemy_units):
                if self.obs[4 * (self.nb_enemy_units + self.nb_my_units) + 1 + 2 * (self.nb_enemy_units * idx1 + idx2)] > 0.5:
                    reward -= 10
                if self.obs_pre[4 * self.nb_my_units + 0 + 4 * idx2] > 0.0 and self.obs[4 * self.nb_my_units + 0 + 4 * idx2] == 0.0:
                    reward += 500
        for idx in range(self.nb_enemy_units):
            if self.obs_pre[4 * self.nb_my_units + 0 + 4 * idx] > self.obs[4 * self.nb_my_units + 0 + 4 * idx]:
                reward -= 15
        if self._check_done():
            if not bool(self.state['battle_won']):
                reward = -300
            else:
                reward = 4000
                self.episode_wins += 1
        if self.episode_steps == self.max_episode_steps:
            reward = -700

        return reward
