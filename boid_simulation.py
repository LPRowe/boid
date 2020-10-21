# -*- coding: utf-8 -*-
"""
Created on Tue Oct 20 19:54:59 2020

@author: rowe1
"""

import pygame
import time

def main():
    
    #Surface settings
    window_width, window_height = 1000, 800
    window_width, window_height = 2000, 1200
    header_body_ratio = 0.8
    bg_width, bg_height = window_width, window_height * header_body_ratio
    gui_width, gui_height = window_width, window_height * (1 - header_body_ratio)
    surface = pygame.display.set_mode((window_width, window_height))
    
    # Import bird image
    bird_width = bird_height = 20
    bird_image = pygame.image.load('./graphics/top_down_bird.png')
    pygame.transform.scale(bird_image, (bird_width, bird_height))
    
    
    #Add GUI Header
    bg_board = [pygame.image.load('./graphics/gui_layout.png')]
    
    for b in bg_board:
        pygame.transform.scale(b, (int(bg_width),int(bg_height)))
    
    #Limit game speed
    sleep_time = 0.03
    
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
        
        surface.blit(bg_board[0],(0, 0))
        
        pygame.display.flip()

    pygame.quit()

if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('Boid Simulation')
    
    main()