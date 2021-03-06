import datetime
import os
import sys

import numpy as np
import random

import agents.image_input.AbstractBrain as AbstractBrain
from agents.networks.dqn_networks import build_dqn_cartpole_network, build_simple_convoluted_net


class Learning(AbstractBrain.AbstractLearning):

    def __init__(self, observations, actions, config):
        super().__init__(observations, actions, config)

        # for classic control environments without any image data
        if self.config['environment'] == 'CartPole-v1':
            self.behaviour_network = build_dqn_cartpole_network(self.state_space, self.action_space, self.config['learning_rate'])
            # create a new network object for the target network
            self.target_network \
                = build_dqn_cartpole_network(self.state_space, self.action_space, self.config['learning_rate'])

        # for atari games
        else:
            self.behaviour_network = build_simple_convoluted_net(self.state_space, self.action_space,
                                                                 self.config['learning_rate'])
            self.target_network = build_simple_convoluted_net(self.state_space, self.action_space,
                                                              self.config['learning_rate'])
        # set values for epsilon-greedy exploration
        self.e_greedy_formula = 'e = min(e_min, e - e_decay)'
        self.epsilon = self.config['epsilon']
        self.epsilon_decay = (self.config['epsilon'] - self.config['epsilon_min']) / self.config['epsilon_explore']

        # copy weights from behaviour to target
        self.update_target_model()

    def update_epsilon(self):
        if self.epsilon > self.config['epsilon_min']:
            self.epsilon = max(self.config['epsilon_min'], self.epsilon - self.epsilon_decay)

    def choose_action(self, state):
        policy = self.behaviour_network.predict(np.expand_dims(state, axis=0))
        if random.random() <= self.epsilon:
            action = random.randrange(self.action_space)
        else:
            action = np.argmax(policy)
        return action, policy[0]

    def train_network(self, states, actions, rewards, next_states, dones, step):
        if step % self.config['network_train_frequency'] == 0:
            target = self.behaviour_network.predict(states)
            next_predictions_network = self.behaviour_network.predict(next_states)
            next_predictions_target = self.target_network.predict(next_states)

            for i in range(self.config['batch_size']):
                if dones[i]:
                    target[i][actions[i]] = rewards[i]
                else:
                    # the key point of Double DQN
                    # selection of action is from model
                    # update is from target model
                    a = np.argmax(next_predictions_network[i])
                    target[i][actions[i]] = rewards[i] + self.config['gamma'] * (next_predictions_target[i][a])

            self.behaviour_network.fit(states, target, batch_size=len(dones), epochs=1, verbose=0)

        # update target network
        if step % self.config['target_update_frequency'] == 0:
            self.update_target_model()
        self.update_epsilon()

    def update_target_model(self):
        self.target_network.set_weights(self.behaviour_network.get_weights())

    def save_network(self, save_path, model_name, timestamp=None):
        # create folder for model, if necessary
        if not os.path.exists(save_path + 'networks/'):
            os.makedirs(save_path + 'networks/')
        if not os.path.exists(save_path + 'target_networks/'):
            os.makedirs(save_path + 'target_networks/')
        # set timestamp if none was specified
        if timestamp is None:
            timestamp = str(datetime.datetime.now())
        # save model weights
        self.behaviour_network.save_weights(save_path + 'networks/' + model_name + '_' + timestamp + '.h5', overwrite=True)
        self.target_network.save_weights(save_path + 'target_networks/' + model_name + '_' + timestamp + '.h5',
                                         overwrite=True)

    def load_network(self, save_path, model_name) -> None:
        if os.path.exists(save_path + 'networks/') and os.path.exists(save_path + 'target_networks/'):
            self.behaviour_network.load_weights(save_path + 'networks/' + model_name)
            self.target_network.load_weights(save_path + 'target_networks/' + model_name)
            print('Loaded model ' + model_name + ' from disk')
        else:
            sys.exit("Model can't be loaded. Model file " + model_name + " doesn't exist at " + save_path + ".")

    def get_test_learner(self):
        test_learner = Learning(self.state_space, self.action_space, self.config)
        # use current network weights for testing
        test_learner.behaviour_network.set_weights(self.behaviour_network.get_weights())
        test_learner.target_network.set_weights(self.target_network.get_weights())
        return test_learner
