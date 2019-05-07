import argparse
import copy
import datetime
import json
import time
from os.path import expanduser

import gym
import tensorflow
from numpy.random import seed
from tensorflow import set_random_seed

import utils.preprocessing.Cartpole_Preprocess as Preprocess
from agents.hybrids.pg_dqn_Brain import Learning
from agents.memory import Memory
from training.testing_functions import test
from utils.storing import save_episode_to_summary
from utils.summary import Summary

seed(2)
set_random_seed(2)

PATH = expanduser("~")
MODEL_FILENAME = ''

summary_frequency = 50
test_frequency = 100


def test_hybrid():
    print('# =========================================== TEST DQN =========================================== #')
    prev_epsilon = learner.dqn_agent.epsilon
    prev_switch = learner.switch

    # don't act randomly
    learner.switch = True
    learner.dqn_agent.epsilon = 0

    test(learner.dqn_agent, copy.deepcopy(env), config, copy.deepcopy(processor),
         MODEL_FILENAME, PATH + '/test_dqn/')

    # ============================================================================================================== #

    print('# =========================================== TEST PG =========================================== #')

    learner.switch = False

    test(learner.pg_agent, copy.deepcopy(env), config, copy.deepcopy(processor),
         MODEL_FILENAME, PATH + '/test_pg/')

    # reset values in case of continued training
    learner.dqn_agent.epsilon = prev_epsilon
    learner.switch = prev_switch


if __name__ == "__main__":
    # combination of run_main and train, adapted for pg+dqn hybrid

    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-file", "--filename", help='name of file containing parameters in json-format', )
    args = parser.parse_args()

    config_file_path = PATH + args.filename
    if config_file_path:
        with open(config_file_path, 'r') as f:
            config = json.load(f)

    # ============================================================================================================== #

    MODEL_FILENAME = MODEL_FILENAME + "CartPole"
    env = gym.make(config['environment'])
    processor = Preprocess.Processor()
    state_space = processor.get_state_space()
    if config['environment'] == 'CartPole-v1':
        state_space = (env.observation_space.shape[0],)
    action_space = env.action_space.n

    # ============================================================================================================== #

    PATH = PATH + '/Gym-T4-Testbed/output/Hybrid/'
    learner = Learning(state_space, action_space, config)

    # ============================================================================================================== #

    dqn_memory = Memory.Memory(config['memory_size'], state_space)
    pg_memory = Memory.Memory(config['memory_size'], state_space)

    # ============================================================================================================== #

    # train learner and plot results
    summary_writer = tensorflow.summary.FileWriter(PATH + 'tensorboard_summary/')
    summary = Summary(['sumiz_step', 'sumiz_reward', 'sumiz_epsilon'],
                      name=MODEL_FILENAME + str(datetime.datetime.now()),
                      save_path=PATH + '/graphs/',
                      min_reward=0,
                      max_reward=500)
    summary_rewards, summary_epsilons, summary_steps = [], [], []

    # ============================================================================================================== #

    training_step = 0

    for episode in range(config['episodes']):

        state = env.reset()
        state = processor.process_state_for_memory(state, True)

        start_time = time.time()
        sum_rewards_array = 0  # total rewards for graphing
        step = 0  # count total steps for each episode for the graph

        while True:
            # perform next step
            action = learner.choose_action(processor.process_state_for_network(state))
            next_state, reward, done, _ = env.step(action)
            reward = processor.process_reward(reward)
            next_state = processor.process_state_for_memory(next_state, False)

            if config['environment'] == 'CartPole-v1':
                # punish if terminal state reached
                if done:
                    reward = -reward
            sum_rewards_array += reward

            # update memories
            dqn_memory.store_transition(state, action, reward, next_state, done)
            pg_memory.store_transition(state, action, reward, next_state, done)

            # update counters
            state = next_state
            step += 1
            training_step += 1

            # train dqn with batch data at every step
            # if len(dqn_memory.stored_transitions) > config['initial_exploration_steps']:
            if len(dqn_memory.stored_transitions) > config['initial_exploration_steps'] and learner.switch:
                states, actions, rewards, next_states, dones = dqn_memory.sample(config['batch_size'], processor)
                learner.train_dqn_network(states, actions, rewards, next_states, dones, training_step)

            if done:

                # print episode results
                print('Completed Episode = ' + str(episode), ' epsilon =', "%.4f" % learner.dqn_agent.epsilon,
                      ', steps = ', step,
                      ", total reward = ", sum_rewards_array)

                # train pg with episode data after every episode
                states, actions, rewards, next_states, dones = pg_memory.sample_all(processor)
                learner.train_pg_network(states, actions, rewards, next_states, dones, step)
                # learner.train_dqn_network(states, actions, rewards, next_states, dones, training_step)

                # update plot summary
                summary_rewards.append(sum_rewards_array)
                summary_steps.append(step)
                summary_epsilons.append(learner.dqn_agent.epsilon)
                if episode % summary_frequency == 0:
                    summary.summarize(step_counts=summary_steps, reward_counts=summary_rewards,
                                      epsilon_values=summary_epsilons,
                                      e_greedy_formula=learner.dqn_agent.e_greedy_formula)
                    summary_rewards, summary_epsilons, summary_steps = [], [], []
                if episode % test_frequency == 0:
                    test_hybrid()
                break

        # ============================================================================================================== #

        # save episode data to tensorboard summary
        if config['save_tensorboard_summary']:
            save_episode_to_summary(summary_writer, episode, step, time.time() - start_time,
                                    sum_rewards_array, learner.epsilon)

    # ============================================================================================================== #

    # update plot summary
    summary.summarize(step_counts=summary_steps, reward_counts=summary_rewards, epsilon_values=summary_epsilons,
                      e_greedy_formula=learner.dqn_agent.e_greedy_formula)

    # ============================================================================================================== #

    test_hybrid()
    env.close()
