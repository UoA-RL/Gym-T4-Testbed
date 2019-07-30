from keras.layers import Input, Concatenate, Conv2D, Flatten, Dense, Conv2DTranspose, Lambda, Reshape
from keras.models import Model
import keras.backend as K

INPUT_DIM = (84,84,4) # 4 stacked frames
Z_DIM = 32
DENSE_SIZE = 1024
ACTION_DIM = (4,1)
LEARNING_RATE = 0.0001
KL_TOLERANCE = 0.5
BATCH_SIZE = 100

def sampling(args):
    z_mean, z_log_var = args
    epsilon = K.random_normal(shape=(K.shape(z_mean)[0], 32), mean=0., stddev=1.0)
    return z_mean + K.exp(z_log_var / 2) * epsilon

class CVAE():
    def __init__(self):
        self.input_dim = INPUT_DIM
        self.z_dim = Z_DIM
        self.action_dim = ACTION_DIM
        self.learning_rate = LEARNING_RATE
        self.kl_tolerance = KL_TOLERANCE   
        self.batch_size = BATCH_SIZE
        
        self.model = self._build() 

    def _build(self):
        # Encoder layers

        action = Input(shape=self.action_dim, name='action_input')          # Input layer for the action, keep separate for calculating reconstruction loss
        vae_action = Dense(4, name='action')(action)                        # 1
        

        # calculate dimensions after convolution by
        #
        #   h = w = (original w + 2*padding - kernel size) / stride
        #

        
        vae_x = Input(shape=self.input_dim, name='observation_input')       # 84x84x4
        h = Conv2D(32, 6, strides=2, activation='relu')(vae_x)              # 40x40x32
        h1 = Conv2D(64, 6, strides=2, activation='relu')(h)                 # 18x18x64
        h2 = Conv2D(128, 6, strides=2, activation='relu')(h1)               # 7x7x128
        h3 = Conv2D(256, 4, strides=2, activation='relu')(h2)               # 2x2x256
        h4 = Flatten()(h3)                                                  # 1024

        h5 = Concatenate([h4, vae_action])                                  # 1025

        # encoder_h = Dense(ENCODER_DIM, activation='relu')()
        z_mean = Dense(self.z_dim, name='z_mean')(h5)            # 32
        z_log_var = Dense(self.z_dim, name='z_log_var')(h5)      # 32
        z = Lambda(sampling, name='sampling')([z_mean, z_log_var])

        # merge latent space with same action vector that was merged into observation
        zc = Concatenate([z, vae_action])

        # Decoder layers
        decoder_dense = Dense(DENSE_SIZE, name='decoder_input')(zc)
        decoder_reshape = Reshape((1,1,1024), name='unflatten')(decoder_dense)
        decoder = Conv2DTranspose(64, 4, strides=2, activation='relu')(decoder_reshape)
        decoder_2 = Conv2DTranspose(64, 4, strides=2, activation ='relu')(decoder)
        decoder_3 = Conv2DTranspose(64, 4, strides=2, activation ='relu')(decoder_2)
        decoder_out = Conv2DTranspose(32, 4, strides=2, activation ='sigmoid')(decoder_3) 
        
        vae_full = Model(vae_x,decoder_out)
        print(vae_full.summary())
        return (vae_full)
    
    def train(self, data):
        self.model.fit(data, data,
                shuffle=True,
                epochs=1,
                batch_size=self.batch_size)
        