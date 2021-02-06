# -*- coding: utf-8 -*-
"""
Created on Tue Oct 20 19:54:59 2020

@author: rowe1
"""

import pygame
import time
import glob
import math, random
from boid_tools import Boid, Boid_Cloud, GUI

class Click_Action(object):
    def __init__(self, action_map):
        self.click_map = {(34, 22, 78, 80):'phi_up',
                          (38, 165, 72, 217):'phi_down',
                          (354, 24, 392, 63):'r_down',
                          (693, 24, 728, 61):'r_up',
                          (361, 99, 394, 138):'rc_down',
                          (692, 100, 725, 137):'rc_up',
                          (361, 182, 395, 214):'max_turn_down',
                          (691, 178, 726, 215):'max_turn_up',
                          (897, 29, 949, 84):'speed_up',
                          (897, 164, 948, 224):'speed_down',
                          (1225, 27, 1272, 85):'num_birds_up',
                          (1221, 166, 1274, 223):'num_birds_down',
                          (1781, 23, 1821, 58):'separation_up',
                          (1394, 27, 1430, 60):'separation_down',
                          (1784, 98, 1820, 135):'alignment_up',
                          (1394, 101, 1430, 137):'alignment_down',
                          (1783, 179, 1816, 214):'cohesion_up',
                          (1393, 179, 1429, 215):'cohesion_down',
                          (1835, 89, 1982, 154):'reset',
                          (1836, 163, 1986, 232):'start'
                          }
        
        self.action_map = {'phi_up': 1,
                          'phi_down': -1,
                          'r_down': -5,
                          'r_up': 5,
                          'rc_down': -0.01,
                          'rc_up': 0.01,
                          'max_turn_down': -1,
                          'max_turn_up': 1,
                          'speed_up': 1,
                          'speed_down': -1,
                          'num_birds_up': None,
                          'num_birds_down': None,
                          'separation_up': 0.01,
                          'separation_down': -0.01,
                          'alignment_up': 0.01,
                          'alignment_down': -0.01,
                          'cohesion_up': 0.01,
                          'cohesion_down': -0.01,
                          'reset': None,
                          'start': None
                          }
    
    def _click_to_action(self, x, y):
        for x1, y1, x2, y2 in self.click_map:
            if x1 <= x <= x2 and y1 <= y <= y2:
                return self.click_map[(x1, y1, x2, y2)]


def main(gui, bird_phi, bird_radius, crit_radius, max_turn, bird_speed, num_birds, separation_coef, alignment_coef, cohesion_coef, sleep_time):
    
    #Surface settings
    window_width, window_height = 2000, 1200
    header_body_ratio = 0.8
    bg_width, bg_height = window_width, window_height * header_body_ratio
    gui_width, gui_height = window_width, int(window_height * (1 - header_body_ratio))
    surface = pygame.display.set_mode((window_width, window_height))
    
    # Import bird images (one image for every 2 degrees ccw from the neg y axis)
    bird_width = bird_height = 50
    bird_image = pygame.image.load('./graphics/top_down_bird_alpha.png') #.png higher res and faster
    bird_images = []
    f = lambda x: (1 + math.sin(2*x)**2) / 4 + (3 / 4)
    variable_scale = True #have birds fluctuate in size based on orientation (looks like elevation change)
    for theta in range(-135,360-135,2): # - 135 so 0 is along the x+ axis
        scale = 1 / f(theta * math.pi / 180) if variable_scale else 1
        w, h = int(bird_width * scale), int(bird_height * scale)
        img = pygame.transform.scale(bird_image, (w, h))
        img = pygame.transform.rotozoom(img, theta, 1)
        bird_images.append(img)
    
    # Bird for radar symbol
    radar_bird = bird_images[45].copy()
    
    #Add GUI Header
    bg_board = pygame.image.load('./graphics/gui_layout.jpg')
    bg_board = pygame.transform.scale(bg_board, (int(gui_width),int(gui_height)))
    bg_board = [bg_board]
    
    # Populate birds
    behavior = (cohesion_coef, separation_coef, alignment_coef)
    boids = []
    for _ in range(num_birds):
        theta = random.randint(0, 359)
        x = random.randint(bird_width, bg_width - bird_width)
        y = gui_height + bird_height + random.randint(0, bg_height - 2*bird_height)
        boids.append(Boid(x, y, theta, bird_speed, bird_radius, bird_phi, 
                          (0, gui_height, window_width-bird_width, window_height-bird_width),
                          (bird_width, bird_height), behavior))
    
    # Track all boids positions and velocities in the boid cloud
    cloud = Boid_Cloud(walls = (0, gui_height, window_width, window_height))
    
    # Convert clicks on gui to actions
    action_map = {'phi_up': bird_phi, 'phi_down': bird_phi,
                  'r_up': bird_radius, 'r_down': bird_radius}
    click = Click_Action(action_map)
    
    run = True
    
    while True:
        if sleep_time:
            time.sleep(sleep_time) #slow down run speed for all algorithms besides A*
        
        event = pygame.event.poll()
        if event.type == pygame.QUIT:
            break
        
        keys=pygame.key.get_pressed()
        if keys[pygame.K_f]:
            sleep_time = max(0, sleep_time - 0.01)
        elif keys[pygame.K_s]:
            sleep_time = min(0.1, sleep_time + 0.01)
        
        #Handle Mouse Clicks for buttons
        mouse = pygame.mouse
        if mouse.get_pressed()[0] and (mouse.get_pos()[1] <= gui_height):
            x,y = mouse.get_pos()
            #print(x,y)
            action = click._click_to_action(x,y)
            if action:
                if action == 'num_birds_up':
                    theta = random.randint(0, 359)
                    x = random.randint(bird_width, bg_width - bird_width)
                    y = gui_height + bird_height + random.randint(0, bg_height-2*bird_height)
                    behavior = (cohesion_coef, separation_coef, alignment_coef)
                    boids.append(Boid(x, y, theta, bird_speed, bird_radius, bird_phi, 
                                      (0, gui_height, window_width-bird_width, window_height-bird_width),
                                      (bird_width, bird_height), behavior))
                    gui.num_birds = len(boids)
                elif action == 'num_birds_down':
                    if len(boids) > 1:
                        boids.pop()
                    gui.num_birds = len(boids)
                elif action == 'reset':
                    for bird in boids:
                        x = random.randint(bird_width, bg_width - bird_width)
                        y = gui_height + bird_height + random.randint(0, bg_height-2*bird_height)
                        bird.x, bird.y = x, y
                elif action == 'start':
                    run = not run
                elif 'phi' in action:
                    bird_phi += 2 if 'up' in action else -2
                    bird_phi = max(0, min(bird_phi, 180))
                    gui.bird_phi = bird_phi
                    gui.generate_radar_points()
                    #print('phi', bird_phi)
                    for bird in boids: bird.phi = bird_phi
                elif 'rc' in action:
                    crit_radius += 0.01 if 'up' in action else -0.01
                    crit_radius = max(0, min(crit_radius, 1))
                    gui.crit_radius = crit_radius
                    gui.generate_radar_points()
                    for bird in boids: bird.crit_radius = crit_radius * bird.radius
                elif 'turn' in action:
                    max_turn += 0.25 if 'up' in action else -0.25
                    max_turn = max(0, min(max_turn, 180))
                    gui.max_turn = max_turn
                    for bird in boids: bird.max_turn = max_turn
                elif 'speed' in action:
                    bird_speed += 0.5 if 'up' in action else -0.5
                    bird_speed = max(0, min(bird_speed, 30))
                    gui.bird_speed = bird_speed
                    for bird in boids: bird.speed = bird_speed
                elif 'r_' in action:
                    bird_radius += 2 if 'up' in action else -2
                    bird_radius = max(0, min(bird_radius, 2000))
                    gui.bird_radius = bird_radius
                    gui.generate_radar_points()
                    for bird in boids: 
                        bird.radius = bird_radius
                        bird.crit_radius = gui.crit_radius * bird.radius
                elif 'separation' in action:
                    separation_coef += 0.02 if 'up' in action else -0.02
                    separation_coef = max(0, min(separation_coef, 1))
                    gui.separation_coef = separation_coef
                    for bird in boids: bird.behavior['social_distancing'] = separation_coef
                elif 'alignment' in action:
                    alignment_coef += 0.02 if 'up' in action else -0.02
                    alignment_coef = max(0, min(alignment_coef, 1))
                    gui.alignment_coef = alignment_coef
                    for boid in boids: bird.behavior['alignment'] = alignment_coef
                elif 'cohesion' in action:
                    cohesion_coef += 0.02 if 'up' in action else -0.02
                    cohesion_coef = max(0, min(cohesion_coef, 1))
                    gui.cohesion_coef = cohesion_coef
                    for bird in boids: bird.behavior['center_of_mass'] = cohesion_coef

                
        elif mouse.get_pressed()[0]:
            # scatter birds
            x,y = mouse.get_pos()
            #print(x, y)
            pass
        
        # =============================================================================
        # Update surface: blit images       
        # =============================================================================
        surface.fill((255, 255, 255))
        
        cloud.update(boids)
        for i,bird in enumerate(boids):
            bird.update(*cloud.visible_birds(bird.x, bird.y, bird.theta, bird.radius, bird.phi, i, bird.crit_radius),
                        cloud.positions,
                        cloud.velocities,
                        cloud.too_close_to_wall,
                        cloud.center_mass)
            bird.draw(surface, bird_images[int(bird.theta // 2) % len(bird_images)])
        surface.blit(bg_board[0], (0, 0))
        gui.draw(surface)
        surface.blit(radar_bird, (202, 97)) # draw bird at center of radar
        pygame.display.flip()

    pygame.quit()

if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('Boid Simulation')
    
    settings = {
                'bird_phi' : 90,       # how wide of an angle can birds see (0 .. 180) phi = 180 is 360 deg vision
                'bird_radius' : 300,    # how far bird can see
                'crit_radius' : 0.5,    # percent of visual radius 
                'max_turn' : 5,         # maximum degrees a bird can turn in one frame
                'bird_speed' : 10,       # pixels / second
                'num_birds' : 20,
                'separation_coef' : 1,  # bird law coefficients
                'alignment_coef' : 1,
                'cohesion_coef' : 1, 
                'sleep_time' : 0,       # limit play speed by pausing sleep_time [ms] between frames
                }
    
    main(gui = GUI(**settings), **settings)