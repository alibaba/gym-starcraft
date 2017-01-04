import logging
from gym.envs.registration import register

logger = logging.getLogger(__name__)

register(
    id='StarCraft-v0',
    entry_point='gym_starcraft.envs:StarCraftEnv',
)
