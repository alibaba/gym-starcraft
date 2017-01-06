import argparse
import numpy as np

import gym_starcraft.utils as utils
import gym_starcraft.envs.starcraft_env as sc


class RandomAgent(object):
    def __init__(self, action_space):
        self.action_space = action_space

    def act(self, observation):
        return self.action_space.sample()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--server', help='server ip')
    args = parser.parse_args()

    env = sc.StarCraftEnv(args.server)
    env.seed(0)
    agent = RandomAgent(env.action_space)

    episode_count = 30
    total_battles = 0

    obs = env.reset()
    while total_battles < episode_count:
        steps = 1
        battles_won = 0
        battles_game = 0
        done = False
        if np.mod(total_battles, 10) == 0:
            battles_won = 0
            battles_game = 0
            obs = env.reset()
        while not done:
            if np.mod(steps, 10) == 0:
                utils.progress(steps, battles_won, battles_game, total_battles)
            action = agent.act(obs)
            obs, reward, done, _ = env.step(action)
            if reward > 0:
                battles_won += 1
            steps += 1
        battles_game += 1
        total_battles += 1

    # Close the env and write monitor result info to disk
    env.close()
