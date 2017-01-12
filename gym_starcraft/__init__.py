from gym.envs.registration import register

register(
    id='StarCraft-v0',
    entry_point='gym_starcraft.envs:StarCraftEnv',
)
