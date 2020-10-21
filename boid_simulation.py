# -*- coding: utf-8 -*-
"""
Created on Tue Oct 20 19:54:59 2020

@author: rowe1
"""

import pygame
import time
import glob
import math, random
from boid_tools import Boid, Boid_Cloud

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
    variable_scale = True #have birds fluctuate in size based on orientation (looks like elevation change)
    for theta in range(-135,360-135,2):
        scale = 1 / f(theta * math.pi / 180) if variable_scale else 1
        w, h = int(bird_width * scale), int(bird_height * scale)
        img = pygame.transform.scale(bird_image, (w, h))
        img = pygame.transform.rotozoom(img, theta, 1)
        bird_images.append(img)
    
    #Add GUI Header
    bg_board = [pygame.image.load('./graphics/gui_layout.png')]
    
    for b in bg_board:
        pygame.transform.scale(b, (int(bg_width),int(bg_height)))
    
    #Limit game speed
    sleep_time = 0
    
    # Set Bird properties
    num_birds = 10
    bird_speed = 15
    bird_radius = 300
    bird_phi = 100
    
    boids = []
    for _ in range(num_birds):
        theta = random.randint(0, 359)
        #theta = 90
        x = random.randint(bird_width, bg_width - bird_width)
        y = gui_height + bird_height + random.randint(0, bg_height-2*bird_height)
        boids.append(Boid(x, y, theta, bird_speed, bird_radius, bird_phi, (0, gui_height, window_width, window_height)))
        
    cloud = Boid_Cloud(wall = (0, gui_height, window_width, window_height))
    
    
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
        
        cloud.update(boids)

        for i,bird in enumerate(boids):
            #bird.theta = (bird.theta + 1) % 360
            bird.update(*cloud.visible_birds(bird.x, bird.y, bird.theta, bird.radius, bird.phi, i, bird.crit_radius),
                        cloud.positions,
                        cloud.velocities,
                        cloud.too_close_to_wall)
            bird.draw(surface, bird_images[int(bird.theta // 2) % len(bird_images)])
        
        surface.blit(bg_board[0], (0, 0))
        
        pygame.display.flip()

    pygame.quit()

if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('Boid Simulation')
    
    main()