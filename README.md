# gym-starcraft
Gym StarCraft is an environment bundle for OpenAI Gym. It is based on [Facebook's TorchCraft](https://github.com/TorchCraft/TorchCraft), which is a bridge between Torch and StarCraft for AI research.

## Installation

1. Install [TorchCraft](https://github.com/TorchCraft/TorchCraft) and its dependencies. You can skip the Torch client part. 

2. Install [OpenAI Gym](https://github.com/openai/gym) and its dependencies.

3. Download and install [torchcraft-py](http://gitlab.alibaba-inc.com/cogcom/torchcraft-py).

4. Install the package itself:
    ```
    git clone http://gitlab.alibaba-inc.com/cogcom/gym-starcraft.git
    cd gym-starcraft
    pip install -e .
    ```