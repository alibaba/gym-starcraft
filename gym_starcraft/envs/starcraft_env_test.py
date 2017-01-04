import argparse
import numpy as np

import starcraft_env
import torchcraft_py.proto as p
import torchcraft_py.utils as utils

parser = argparse.ArgumentParser()
parser.add_argument('-s', '--server', help='server ip')
args = parser.parse_args()
print args


def play_game():
    total_battles = 0
    battles_won = 0
    battles_game = 0
    env = starcraft_env.StarCraftEnv(args.server)
    while total_battles < 40:
        nloop = 1
        obs = None
        if np.mod(total_battles, 10) == 0:
            battles_won = 0
            battles_game = 0
            obs = env.reset()
        done = False
        while not done:
            utils.progress(nloop, battles_won, battles_game, total_battles)
            nloop += 1
            action = get_action(obs)
            obs, reward, done, info = env.step(action)
            if reward > 0:
                battles_won += 1
        battles_game += 1
        total_battles += 1
    env.close()


def get_action(state):
    action = []
    if state is None:
        return action

    for uid, ut in state['units_myself'].iteritems():
        target = utils.get_weakest(state['units_enemy'])
        if target != -1:
            action.append(
                p.concat_cmd(p.commands['command_unit_protected'], uid,
                             p.unit_command_types['Attack_Unit'], target))
    return action


if __name__ == '__main__':
    play_game()
