import argparse
import gym_starcraft.envs.single_battle_env as sc


class HumanAgent(object):
    def __init__(self, action_space):
        self.action_space = action_space

    def act(self):
        return None


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--ip', help='server ip')
    parser.add_argument('--port', help='server port', default="11111")
    args = parser.parse_args()

    env = sc.SingleBattleEnv(args.ip, args.port, speed=60)
    env.seed(123)
    agent = HumanAgent(env.action_space)

    episodes = 0
    while True:
        obs = env.reset()
        done = False
        while not done:
            action = agent.act()
            obs, reward, done, info = env.step(action)
        episodes += 1

    env.close()
