# -*- coding: utf-8 -*-
"""
Created on Tue Oct 20 19:54:59 2020

@author: rowe1
"""

import pygame
import time
import glob
import math, random
from boid_tools import Boid

def main():
    
    #Surface settings
    window_width, window_height = 1500, 1000
    window_width, window_height = 2000, 1200
    header_body_ratio = 0.8
    bg_width, bg_height = window_width, window_height * header_body_ratio
    gui_width, gui_height = window_width, window_height * (1 - header_body_ratio)
    surface = pygame.display.set_mode((window_width, window_height))
    
    # Import bird images (one image for every 2 degrees ccw from the neg y axis)
    bird_width = bird_height = 50
    bird_image = pygame.image.load('./graphics/top_down_bird_alpha.png')
    bird_images = []
    f = lambda x: (1 + math.sin(2*x)**2) / 4 + (3 / 4)
    variable_scale = True
    for theta in range(-45,360-45,2):
        scale = 1 / f(theta * math.pi / 180) if variable_scale else 1
        w, h = int(bird_width * scale), int(bird_height * scale)
        img = pygame.transform.scale(bird_image, (w, h))
        img = pygame.transform.rotozoom(img, theta, 1)
        bird_images.append(img)
    
    '''
    # Import bird images (one image for every 2 degrees ccw from the neg y axis)
    bird_width = bird_height = 50
    bird_files = glob.glob('./graphics/rotated_birds/*')
    bird_files.sort(key = lambda name: int(name.split('rotated_birds\\')[-1].split('_')[0]))
    bird_images = []
    f = lambda x: (1 + math.sin(2*x)**2) / 4 + (3 / 4)
    for name in bird_files:
        theta = int(name.split('rotated_birds\\')[-1].split('_')[0])
        img = pygame.image.load(name)
        scale = 1 / f(theta * math.pi / 180)
        w, h = int(bird_width * scale), int(bird_height * scale)
        img = pygame.transform.scale(img, (w, h))
        img.set_colorkey((0, 0, 0, 0))
        bird_images.append(img)
    '''
    #Add GUI Header
    bg_board = [pygame.image.load('./graphics/gui_layout.png')]
    
    for b in bg_board:
        pygame.transform.scale(b, (int(bg_width),int(bg_height)))
    
    #Limit game speed
    sleep_time = 0.03
    
    num_birds = 100
    bird_speed = 10
    boids = []
    for _ in range(num_birds):
        theta = random.randint(0, 359)
        x = random.randint(bird_width, bg_width - bird_width)
        y = gui_height + bird_height + random.randint(0, bg_height-2*bird_height)
        boids.append(Boid(x, y, theta, bird_speed))
    
    
    while True:
        time.sleep(sleep_time) #slow down run speed for all algorithms besides A*
        
        event = pygame.event.poll()
        if event.type == pygame.QUIT:
            break
        
        keys=pygame.key.get_pressed()
        if keys[pygame.K_f]:
            pass
        
        #Handle Mouse Clicks for buttons
        mouse = pygame.mouse
        if mouse.get_pressed()[0] and (mouse.get_pos()[1] <= gui_height):
            x,y = mouse.get_pos()
            pass
        
        surface.fill((255, 255, 255))
        for bird in boids:
            bird.theta = (bird.theta + 1) % 360
            bird.draw(surface, bird_images[bird.theta // 2])
        
        surface.blit(bg_board[0], (0, 0))
        
        pygame.display.flip()

    pygame.quit()

if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('Boid Simulation')
    
    main()