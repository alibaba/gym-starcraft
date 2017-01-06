from setuptools import setup

setup(name='gym_starcraft',
      version='0.0.1',
      description='OpenAI Gym environment for StarCraft based on TorchCraft',
      license='MIT License',
      install_requires=['gym>=0.2.3', 'keras_rl>=0.2.0rc1', 'keras>=1.2.0'])
