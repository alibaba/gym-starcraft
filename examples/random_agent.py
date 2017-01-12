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
    parser.add_argument('--ip', help='server ip')
    parser.add_argument('--port', help='server port')
    args = parser.parse_args()

    env = sc.StarCraftEnv(args.ip, args.port, 2000)
    env.seed(123)
    agent = RandomAgent(env.action_space)

    episodes = 0
    wins = 0
    while episodes < 50:
        steps = 0
        obs = env.reset()
        done = False
        while not done:
            action = agent.act(obs)
            obs, reward, done, info = env.step(action)
            if info['battle_won']:
                wins += 1
            steps += 1
        episodes += 1

    env.close()
