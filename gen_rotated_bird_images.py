# -*- coding: utf-8 -*-
"""
Created on Tue Oct 20 22:20:20 2020

@author: rowe1
"""

from PIL import Image

img_path = './graphics/top_down_bird.png'
save_dir = './graphics/rotated_birds/'
img = Image.open(img_path)

def rotate_img(degrees):
    return img.rotate(degrees, expand=1)

for theta in range(-45, 359-45, 2):
    print(theta)
    rotated_image = rotate_img(theta)
    rotated_image.save(save_dir+str(theta+45)+'_bird.png')