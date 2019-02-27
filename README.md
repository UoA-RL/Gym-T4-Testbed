# Gym-T4-Testbed

- trying to write our own algorithms for gym environments
- setting up benchmark system to run algorithms on various OpenAI environments
----------------
### Dependencies 

- Python 3.6
- Numpy 1.15
- Tensorflow 
- Keras
- OpenAI Gym Atari
- scikit-image
- OpenCV
- matplotlib
- imageio

----------------
### Files Overview

``` bash

# Bash scripts
    run.sh
    
    runme.sh 
    testbed.txt

# Execution scripts 
    run_main.py

# Environment State Preprocessing
    /Preprocess     # folder
        Cartpole_Preprocess.py
        Pong_Preprocess.py
        _Preprocess
        _Preprocess
        _Preprocess

# RL Algorithms
    /DQN
        brain.py
        network.py

# Saving training data
    


```



----------------


| Envrionment   | Algorithm | Required Training Episodes |
| --------------------- | ------------------- |------------------- |
| { Toy text } |   NB. *many environments do not render*|
|- Roulette-v0      |Q Learning|
|   |  |
|{ Atari }      ||
|- Pong-v0        | Double DQN, policy gradient| 10 000
|- Breakout-v0       | Double DQN| 500 000 pure exploitation, train for 1000 000 episodes | 
|- SpaceInvaders-v0       |DQN|
|- MsPacman-v0||
|- Enduro-v0||
|- Super mario||
|||
|{ Algorithms } | NB. *difficult action spaces* |
| - Copy-v0 | |
|||
|{ Box 2D }
|||
|VizDoom
|||
|{ MuJoCo }
|||
|{ Robotics }
