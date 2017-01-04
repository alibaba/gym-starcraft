import gym

from torchcraft_py import torchcraft
from torchcraft_py import proto

DEBUG = 0
SPEED = 0
FRAME_SKIP = 0


class StarCraftEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self, server_ip):
        self.client = torchcraft.Client(server_ip)

    def __del__(self):
        self.client.close()

    def _step(self, action):
        self._send_action(action)
        self._recv_state()

        obs = self._get_obs()
        reward = self._get_reward()
        done = self._get_status()

        return obs, reward, done, {}

    def _send_action(self, action):
        self.client.send(action)

    def _recv_state(self):
        self.client.receive()

    def _get_reward(self):
        if bool(self.client.state.d['battle_won']):
            return 1
        return 0

    def _get_obs(self):
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

    def _render(self, mode='human', close=False):
        pass
