import gym

import torchcraft_py.torchcraft as tc
import torchcraft_py.proto as proto
import gym_starcraft.utils as utils


class StarCraftEnv(gym.Env):
    def __init__(self, server_ip, server_port, speed, frame_skip, self_play,
                 max_episode_steps):
        self.client = tc.Client(server_ip, server_port)
        self.state = self.client.state.d

        self.speed = speed
        self.frame_skip = frame_skip
        self.self_play = self_play
        self.max_episode_steps = max_episode_steps

        self.episodes = 0
        self.episode_wins = 0
        self.episode_steps = 0

        self.action_space = self._action_space()
        self.observation_space = self._observation_space()

        self.state = None
        self.obs = None
        self.obs_pre = None

    def __del__(self):
        self.client.close()

    def _step(self, action):
        self.episode_steps += 1

        self.client.send(self._make_commands(action))
        self.client.receive()
        self.state = self.client.state.d
        self.obs = self._make_observation()
        reward = self._compute_reward()
        done = self._check_done()
        info = self._get_info()

        self.obs_pre = self.obs
        return self.obs, reward, done, info

    def _reset(self):
        utils.print_progress(self.episodes, self.episode_wins)

        if not self.self_play and self.episode_steps == self.max_episode_steps:
            self.client.send([proto.concat_cmd(proto.commands['restart'])])
            self.client.receive()
            while not bool(self.client.state.d['game_ended']):
                self.client.send([])
                self.client.receive()

        self.episodes += 1
        self.episode_steps = 0

        self.client.close()
        self.client.connect()
        setup = [proto.concat_cmd(proto.commands['set_speed'], self.speed),
                 proto.concat_cmd(proto.commands['set_gui'], 1),
                 proto.concat_cmd(proto.commands['set_frameskip'],
                                  self.frame_skip),
                 proto.concat_cmd(proto.commands['set_cmd_optim'], 1)]
        self.client.send(setup)
        self.client.receive()
        self.state = self.client.state.d

        self.obs = self._make_observation()
        self.obs_pre = self.obs
        return self.obs

    def _action_space(self):
        """Returns a space object"""
        raise NotImplementedError

    def _observation_space(self):
        """Returns a space object"""
        raise NotImplementedError

    def _make_commands(self, action):
        """Returns a game command list based on the action"""
        raise NotImplementedError

    def _make_observation(self):
        """Returns a observation object based on the game state"""
        raise NotImplementedError

    def _compute_reward(self):
        """Returns a computed scalar value based on the game state"""
        raise NotImplementedError

    def _check_done(self):
        """Returns true if the episode was ended"""
        return bool(self.state['game_ended']) or self.state['battle_just_ended']

    def _get_info(self):
        """Returns a dictionary contains debug info"""
        return {}

    def render(self, mode='human', close=False):
        pass
