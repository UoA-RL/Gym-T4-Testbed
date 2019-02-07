import keras
from keras.models import Sequential
from keras.layers import Dense, Flatten, Conv2D


class neural_net():
    def __init__(self, obs_space, action_space):
        self.obs_space = obs_space
        self.action_space = action_space
        self.model = Sequential()
        # initialise network object
        neural_net.build_network(self)

    def build_network(self):
        # 3 layers of convolutional networks
        # padding is added so that information is not loss when the kernal size is smaller
        self.model.add(Conv2D(32, kernel_size=(8, 8), strides = (2, 2), padding='valid', activation = 'relu', input_shape=self.obs_space, data_format='channels_first'))
        self.model.add(Conv2D(64, kernel_size=(4, 4), strides = (2, 2), padding='valid', activation = 'relu', data_format='channels_first'))
        self.model.add(Conv2D(64, kernel_size=(3, 3), strides = (2, 2), padding='valid', activation = 'relu', data_format='channels_first'))
        # convert image from 3D to 1D
        self.model.add(Flatten())

        # hidden layer takes a pre-processed frame as input, and has 200 units
        #  fibre channel layer 1
        self.model.add(Dense(units=12,input_dim=self.obs_space, activation='relu', kernel_initializer='glorot_uniform'))

        # output layer
        self.model.add(Dense(units=self.action_space, activation='sigmoid', kernel_initializer='RandomNormal'))

        # compile the model using traditional Machine Learning losses and optimizers
        # self.model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
        self.model.compile(loss='mse', optimizer='adam', metrics=['accuracy'])

        # self.model.summary()

    