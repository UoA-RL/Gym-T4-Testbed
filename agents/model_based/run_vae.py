# from vae import VAE
import gym
import os
import cv2
from vae import VAE
import numpy as np

image = cv2.imread('./resized_img.jpg')
print(image.shape)

vae = VAE()
vae.set_weights('./vae_weights.h5')

# Need to give the input an extra dimension since model.predict() expects batch size as well [batch_size, img_height, img_width, channels]
image = np.expand_dims(image,axis = 0)
predicted_image = vae.predict(image)

# Have to remove the extra layer and multiply rgb values by 255 to get the original image since before we divided by 255 during storage
image_vector = predicted_image[0,:,:,:]*255

cv2.imwrite('./predicted.jpg', predicted_image[0,:,:,:]*255)

