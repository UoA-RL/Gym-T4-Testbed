from collections import deque
from skimage import transform # Help us to preprocess the frames
from skimage.color import rgb2gray # Help us to gray our frames
import numpy as np
import matplotlib.pyplot as plt

class Processing:
    def __init__(self):
        self.deque = deque([np.zeros((110,84), dtype=np.int) for i in range(4)], maxlen=4)
        self.step_max = 2000
        self.time_max = 30
        self.reward_min = 0       
        self.reward_max= 1000

    def Preprocessing(self, state, is_new_episode):
        # plt.imshow(np.array(state))
        # plt.show()
        # grayscale
        frame = rgb2gray(state)
        frame=frame[35:195]              
        frame = frame / 255.0 
        frame= transform.resize(frame,[110,84])
        

        plt.imshow(np.array(frame))
        plt.show()
        
        frame = self.frames_to_state(frame, is_new_episode)
        return frame


    def frames_to_state(self, frame, is_new_episode):

        # print(frame.shape[:])
        # frame = self.Preprocessing(self, state)
        if is_new_episode:
            # all frames in new deque are of same state
            self.deque.append(frame)
            self.deque.append(frame)
            self.deque.append(frame)
            self.deque.append(frame)

        else:
            self.deque.append(frame)
            
        # reshape the deque
        stacked_state = np.stack(self.deque, axis = 0)

        return stacked_state


    def get_state_space(self):
        return np.shape(self.deque) 

    def discounted_rewards(self, rewards, gamma):
        return rewards

    def new_action_space(self,actions):
        return actions

    def mapping_actions_to_keys(self,action_taken):            
        return action_taken