import numpy as np
import random
from collections import deque
from DQN.Network import neural_net
import time 

MAX_MEMORY_LENGTH = 6000
LEARNING_RATE = 0.1
REWARD_DECAY = 0.8	
START_TRAINING = 5000
batch_size=32

class Learning():


    def __init__(self,observations, actions):
        self.state_space = observations 
        self.action_space = actions

        self.network = neural_net(self.state_space, self.action_space)
        
        self.epsilon = 0
        self.gamma = REWARD_DECAY
        self.alpha = 0.86
        #transitions is where we store memory of max memory length
        self.transitions = deque(maxlen = MAX_MEMORY_LENGTH)

    # the processed state is used in choosing action
    def choose_action(self, state, episode):
        if random.random() > self.epsilon:
            action = random.randrange(self.action_space)
        else:
            action = np.argmax(self.network.model.predict(np.expand_dims(state, axis = 0)))
            ACT_VALUES=self.network.model.predict(np.expand_dims(state, axis = 0))
            # action = np.argmax(ACT_VALUES[0])
            # if self.network.model.predict(np.expand_dims(state, axis = 0)).any() < 0:
            # print('episode ', episode, ' has negative')
            print('Episode ', episode, ': q values:  ', ACT_VALUES)
            print('Episode ', episode, ': action:  ', action)

        # decay epsilon
        # if episode > 3000:
        	# self.epsilon = 1 - 3 ** (-0.00023 * (episode - 3000))
        # self.epsilon = 1 - 3 ** (-0.00023 * episode)

        self.epsilon = 1 - 5 ** (-0.003 * (episode - 6))
        return action

    # def back_propagate(self):




    def memory_replay(self):
        # experience replay learning from our memories
        if len(self.transitions) < START_TRAINING:
            return

        # if len(self.transitions) > MAX_MEMORY_LENGTH:
        #     sample_index = np.random.choice(self.memory_size, size=self.batch_size)
        # else:
        #     sample_index = np.random.choice(self.memory_counter, size=self.batch_size)
        # batch = self.memory[sample_index, :]

        # experience replay
        batch = random.sample(self.transitions, batch_size)
        # print(np.shape(self.transitions))
        # print('batch states =', batch[0][0])
        # print('batch actions =', batch[0][1])
        # print('batch rewards =', batch[0][2])
        # print('batch next state =', batch[0][3])
        # print('batch dones =', batch[0][4])
        #print(np.shape(batch))
        ###############################################################################################
        # initialise arrays

    #     states = np.zeros((batch_size, *self.state_space)) 
    #     next_states = np.zeros((batch_size, *self.state_space))
    #     action, reward, done = [], [], []

    # #     # extract variables from transition
    # #     # extract seperate s,a,r.s'
    #     for i in range(batch_size):
    #         states[i] = batch[i][0]
    #         action.append(batch[i][1])
    #         reward.append(batch[i][2])
    #         next_states[i] = batch[i][3]
    #         done.append(batch[i][4])  

    #         target = self.network.model.predict(states, batch_size=batch_size)
    #         target_next = self.network.model.predict(next_states, batch_size=batch_size)
    # #         # print(np.shape(target))
    # #         # time.sleep(10)
    # # ###############################################################################################

    #     for sample in range(batch_size):
    #         # check if transition was at end of episode
    #         is_done = done[sample]
    #         if is_done:
    #             target[sample][action[sample]] = reward[sample]
    #         else:
    #             # Bellman Equation
    #             target[sample][action[sample]] = reward[sample] + self.gamma * np.max(target_next[sample])
        
    #         #                                      A   
    #         # [Obseravations -> [predicted , R or R + predicted% , predicted]]

    #         # calculates loss and does optimisation
    #         # run graph
    #         # Predicted Q -> Actual Q
    #         n = np.expand_dims(states[sample], axis= 0)
    #         # print(np.shape(n))
    #         # print(np.shape(target[sample]))
    #         # print(target[sample])
    #         # a = np.expand_dims(target[sample], axis= 1)
    #         # self.network.model.fit(n, target[sample],batch_size = batch_size, verbose=0)

    #         self.network.model.fit(states, target,batch_size = batch_size, verbose=0)


        # ======================================================================================

        for state, action, reward, next_state, done in batch:
            target = reward
            if not done:
                next_state = np.expand_dims(next_state, axis= 0)
                #print('np.shape(next_state) =', np.shape(next_state) )
                print('next_state) =',  np.expand_dims(next_state, axis= 0))
                target = reward + self.gamma * np.max(self.network.model.predict(next_state))


            state = np.expand_dims(state, axis=0)
            #print('np.shape(state)', np.shape(state))
            target_f = self.network.model.predict(state)
            
            target_f[0][action] = target
            print('target_f =', target_f)
            self.network.model.fit(state, target_f, verbose = 0)

        print("finish replay")

