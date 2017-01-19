# gym-starcraft
Gym StarCraft is an environment bundle for OpenAI Gym. It is based on [Facebook's TorchCraft](https://github.com/TorchCraft/TorchCraft), which is a bridge between Torch and StarCraft for AI research.

## Installation

1. Install [OpenAI Gym](https://github.com/openai/gym) and its dependencies.

2. Install [TorchCraft](https://github.com/TorchCraft/TorchCraft) and its dependencies. You can skip the torch client part. 

3. Install [torchcraft-py](https://github.com/deepcraft/torchcraft-py) and its dependencies.

4. Install the package itself:
    ```
    git clone https://github.com/deepcraft/gym-starcraft.git
    cd gym-starcraft
    pip install -e .
    ```

## Usage
1. Start StarCraft server with BWAPI by Chaoslauncher.

2. Run examples:

    ```
    cd examples
    python random_agent.py --ip $server_ip --port $server_port 
    ```
    
    The `$server_ip` and `$server_port` are the ip and port of the server running StarCraft.   
    
