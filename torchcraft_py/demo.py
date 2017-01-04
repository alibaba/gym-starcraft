import argparse

import proto
import torchcraft as tc
import utils

DEBUG = 0

total_battles = 0
nrestarts = -1

parser = argparse.ArgumentParser()
parser.add_argument('-s', '--server', help='server ip')
args = parser.parse_args()
print args

while total_battles < 40:
    nloop = 1
    battles_won = 0
    battles_game = 0

    print ""
    print "GAME STARTED"

    # Create a client and connect to the TorchCraft server
    client = tc.Client(args.server)
    init = client.connect()
    if DEBUG > 0:
        print "Received init: " + init

    # Setup the game
    setup = [proto.concat_cmd(proto.commands['set_speed'], 0),
             proto.concat_cmd(proto.commands['set_gui'], 1),
             proto.concat_cmd(proto.commands['set_cmd_optim'], 1)]
    if DEBUG > 0:
        print "Setting up the game: " + ':'.join(setup)
    client.send(setup)

    while True:
        # Print the progress
        utils.progress(nloop, battles_won, battles_game, total_battles)

        update = client.receive()
        if DEBUG > 0:
            print "Received state: " + update

        nloop += 1
        actions = []
        if bool(client.state.d['game_ended']):
            if DEBUG > 0:
                print "GAME ENDED"
            break
        elif client.state.d['battle_just_ended']:
            if DEBUG > 0:
                print "BATTLE ENDED"
            if bool(client.state.d['battle_won']):
                battles_won += 1
            battles_game += 1
            total_battles += 1
            if battles_game >= 10:
                actions = [proto.concat_cmd(proto.commands['restart'])]
        elif client.state.d['waiting_for_restart']:
            if DEBUG > 0:
                print("WAITING FOR RESTART")
        else:
            for uid, ut in client.state.d['units_myself'].iteritems():
                target = utils.get_weakest(client.state.d['units_enemy'])
                if target != -1:
                    actions.append(
                        proto.concat_cmd(
                            proto.commands['command_unit_protected'], uid,
                            proto.unit_command_types['Attack_Unit'], target))

        if DEBUG > 0:
            print "Sending actions: " + str(actions)

        client.send(actions)

    client.close()
