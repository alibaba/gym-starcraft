import argparse
import time
import numpy as np

from keras.models import Sequential, Model
from keras.layers import Dense, Activation, Flatten, Input, merge
from keras.optimizers import Adam

from rl.agents import DDPGAgent
from rl.memory import SequentialMemory
from rl.random import OrnsteinUhlenbeckProcess

import gym_starcraft.envs.starcraft_env as sc

parser = argparse.ArgumentParser()
parser.add_argument('-s', '--server', help='server address')
args = parser.parse_args()
print args
if args.server:
    SERVER_IP = args.server

timestamp = time.strftime("%Y%m%d%H%M%S")
nb_episode_steps = 2000

# Get the environment and extract the number of actions.
env = sc.StarCraftEnv(args.server, nb_episode_steps)
np.random.seed(123)
env.seed(123)
ENV_NAME = "StarCraft"
nb_actions = env.action_space.shape[0]
nb_states = env.observation_space.shape[0]

# Next, we build a very simple model.
actor = Sequential()
actor.add(Flatten(input_shape=(1,) + env.observation_space.shape))
actor.add(Dense(16))
actor.add(Activation('relu'))
actor.add(Dense(16))
actor.add(Activation('relu'))
actor.add(Dense(16))
actor.add(Activation('relu'))
actor.add(Dense(nb_actions))
actor.add(Activation('tanh'))
print(actor.summary())

action_input = Input(shape=(nb_actions,), name='action_input')
observation_input = Input(shape=(1,) + env.observation_space.shape,
                          name='observation_input')
flattened_observation = Flatten()(observation_input)
x = merge([action_input, flattened_observation], mode='concat')
x = Dense(32)(x)
x = Activation('relu')(x)
x = Dense(32)(x)
x = Activation('relu')(x)
x = Dense(32)(x)
x = Activation('relu')(x)
x = Dense(1)(x)
x = Activation('linear')(x)
critic = Model(input=[action_input, observation_input], output=x)
print(critic.summary())

# Finally, we configure and compile our agent.
memory = SequentialMemory(limit=100000, window_length=1)
random_process = OrnsteinUhlenbeckProcess(theta=.15, mu=0., sigma=.3, size=3)
agent = DDPGAgent(nb_actions=nb_actions, actor=actor, critic=critic,
                  critic_action_input=action_input,
                  memory=memory, nb_steps_warmup_critic=100,
                  nb_steps_warmup_actor=100,
                  random_process=random_process, gamma=.99,
                  target_model_update=1e-3)
agent.compile(Adam(lr=.001, clipnorm=1.), metrics=['mae'])

agent.load_weights('ddpg_{}_weights.h5f'.format(ENV_NAME))

# Okay, now it's time to learn something!
agent.fit(env, nb_steps=40000, visualize=True, verbose=2,
          nb_max_episode_steps=nb_episode_steps)

# After training is done, we save the final weights.
agent.save_weights('ddpg_{}_weights.h5f'.format(ENV_NAME), overwrite=True)
agent.save_weights('ddpg_{}_weights_{}.h5f'.format(ENV_NAME, timestamp),
                   overwrite=True)

# Finally, evaluate our algorithm for 10 episodes.
agent.test(env, nb_episodes=2, visualize=True,
           nb_max_episode_steps=nb_episode_steps)
