# -*- coding: utf-8 -*-
"""
Created on Tue Oct 20 22:08:16 2020

@author: rowe1
"""

import pygame
import math
import functools
import numpy as np

class GUI(object):
    def __init__(self, bird_phi, bird_radius, crit_radius, max_turn, bird_speed, num_birds, separation_coef, alignment_coef, cohesion_coef, sleep_time):
        
        # Bird params
        self.bird_phi = bird_phi
        self.bird_radius = bird_radius
        self.bird_speed = bird_speed
        self.crit_radius = crit_radius
        self.max_turn = max_turn
        self.num_birds = num_birds
        self.separation_coef = separation_coef
        self.alignment_coef = alignment_coef
        self.cohesion_coef = cohesion_coef
        
        # Font
        self.font = pygame.font.SysFont('tahoma', 35, bold=True)
        self.med_font = pygame.font.SysFont('tahoma', 26, bold=True)
        self.small_font = pygame.font.SysFont('tahoma', 18, bold=True)
        self.font_color = (255,255,255)
        self.offset = 28
        
        # Bird Radar (only affects radar image on gui)
        self.radar_center = (232, 124)                   # center of bird radar image
        self.max_rad = 110                               # max radius of radar image [pixels]
        self.theta_offset = -math.pi / 2                  # to help orient the radar vertically
        self.generate_radar_points() # points for bird radar polygon
        self.radar_color = (88, 214, 141)
        self.crit_radar_color = (255, 124, 124)
        
    def generate_radar_points(self):
        phi = self.bird_phi * math.pi / 180
        radar_thetas = np.linspace(-phi + self.theta_offset, phi + self.theta_offset, 120)
        radar_radius = self.max_rad if self.bird_radius >= 500 else self.max_rad * self.bird_radius / 500
        xc, yc = self.radar_center
        self.radar_points = [self.radar_center] + [(int(xc + radar_radius * math.cos(t)), 
                                                    int(yc + radar_radius * math.sin(t))) for t in radar_thetas]
        self.crit_radar_points = [self.radar_center] + [(int(xc + self.crit_radius * radar_radius * math.cos(t)), 
                                                         int(yc + self.crit_radius * radar_radius * math.sin(t))) for t in radar_thetas]
    
    def draw(self, surface):
        
        # Radar Polygon
        pygame.draw.polygon(surface, self.radar_color, self.radar_points)
        
        # Radar Crit Radius
        pygame.draw.polygon(surface, self.crit_radar_color, self.crit_radar_points)

        # R
        text_radius = self.font.render(str(int(self.bird_radius)) + " pixels", 1, self.font_color)
        surface.blit(text_radius, (459,48-self.offset))
        
        # Rc
        text_crit = self.font.render(str(int(100 * self.crit_radius)) + " %", 1, self.font_color)
        surface.blit(text_crit, (480,125-self.offset))
        
        # Max Turn
        text_turn = self.font.render(str(int(self.max_turn)), 1, self.font_color)
        text_deg = self.small_font.render("o", 1, self.font_color)
        surface.blit(text_turn, (598,201-self.offset))
        surface.blit(text_deg, (598 + text_turn.get_width(), 201 - 1.2*self.offset))
        
        # num_birds
        text_num_birds = self.font.render(str(self.num_birds), 1, self.font_color)
        surface.blit(text_num_birds, (1254, 127 - self.offset))
        
        # Separation
        text_sep = self.font.render(str(int(100 * self.separation_coef)) + str('%'), 1, self.font_color)
        surface.blit(text_sep, (1667, 50 - self.offset))
        
        # Alignment
        text_align = self.font.render(str(int(100 * self.alignment_coef)) + str('%'), 1, self.font_color)
        surface.blit(text_align, (1651, 126 - self.offset))
        
        # Cohesion
        text_cohesion = self.font.render(str(int(100 * self.cohesion_coef)) + str('%'), 1, self.font_color)
        surface.blit(text_cohesion, (1620, 201 - self.offset))
        
        # Cohesion
        text_speed = self.med_font.render(str(int(self.bird_speed)) + " pixels/frame", 1, self.font_color)
        surface.blit(text_speed, (851, 125 - 0.5*self.offset))

class Boid_Cloud(object):
    def __init__(self, walls = (0, 240, 2000, 1200)):
        '''
        Store single instant data for all boids
        Helpful for tweaking single boids based on other boid's behavior without
        having adverse behavior caused by the order in which boids are updated
        '''
        self.positions = []
        self.velocities = []
        self.too_close_to_wall = set()
        self.x_min, self.y_min, self.x_max, self.y_max = walls
        self.crit_radius = 100
        self.center_mass = [(self.x_min + self.x_max) // 2, (self.y_min + self.y_max) // 2] # center of mass of all the boids initialized as screen center
    
    def update(self, boid_list):
        self.positions = []
        self.velocities = []
        self.too_close_to_wall = set()
        self.center_mass = [0, 0]
        for i, bird in enumerate(boid_list):
            x, y = bird.x, bird.y
            self.center_mass[0] += x
            self.center_mass[1] += y
            self.positions.append((x,y))
            self.velocities.append(bird.get_vel())
            
            # If bird is too close to the wall, moving away from the wall will take priority
            if (x < self.x_min + self.crit_radius) or (y < self.y_min + self.crit_radius) or \
                (x > self.x_max - self.crit_radius) or (y > self.y_max - self.crit_radius):
                self.too_close_to_wall.add(i)
    
    def visible_birds(self, x, y, theta, radius, phi, j, crit_radius):
        '''
        In: (x, y): birds position
            theta:  birds orientation
            radius: how far the bird can see
            phi:    how wide of an angle the bird can see (0 .. 180 degrees)
            j:      index of the current bird (ignore self)
        
        returns list of visible birds by index
        '''
        visible = set()
        too_close = set()
        for i,(x2,y2) in enumerate(self.positions):
            if i != j: 
                R = ((x2 - x) ** 2 + (y2 - y) ** 2) ** 0.5
                if R <= radius:
                    theta -= 90 # to orient with x + axis
                    theta_low = theta - phi
                    theta_high = theta + phi
                    theta_bird = math.atan2(y2 - y, x2 - x) * 180 / math.pi
                    theta_low, theta_high = sorted((theta_low % 360, theta_high % 360))
                    if theta_low <= theta_bird % 360 <= theta_high:
                        visible.add(i)
                        if R < crit_radius:
                            too_close.add(i)
        return visible, too_close
    
    
class Boid(object):
    def __init__(self, x, y, theta, s, radius = 100, phi = 150, walls = (0, 240, 2000, 1200)):
        # Position / velocity params
        self.x = x
        self.y = y
        self.theta = theta
        self.speed = s
        
        # vision params
        self.radius = radius # can see all birds within self.radius pixel radius
        self.phi = phi # cannot see birds in the 60 degree window behind it
        
        # control params: what does the bird consider when updating it's movement
        self.behavior = {'center_of_mass': .25,    # steer towards the center of mass of neighbors (weight 0 .. 1)
                         'social_distancing': 1, # don't get too close to neighbors (weight 0 .. 1)
                         'alignment': 1}         # match neighbor's velocity vector (weight 0 .. 1)
        
        # turning and velocity change capabilities
        self.max_turn = 3 # cannot change more than 10 degrees in 1 frame
        self.max_acceleration = 0.2 # cannot change speed by more than 20% in 1 frame
        
        # bounds boid should not cross
        self.x_min, self.y_min, self.x_max, self.y_max = walls
        self.y_mid = (self.y_min + self.y_max) // 2
        self.x_mid = (self.x_min + self.x_max) // 2
        self.crit_radius = 0.4 * radius # the point at which birds repel from one another
        
    def draw(self, surface, image):
        surface.blit(image, (self.x, self.y))
    
    def get_vel(self):
        '''
        Returns current (x_vel, y_vel) for boid
        '''
        #theta = (self.theta - 90) % 360 # because self.theta is wrt y- axis
        theta = self.theta
        x_vel = self.speed * math.cos(theta * math.pi / 180)
        y_vel = -1 * self.speed * math.sin(theta * math.pi / 180) # remember down is positive for y
        return (x_vel, y_vel)
    
    def center_mass(self, visible_birds, bird_positions):
        '''
        returns the center of mass of all of the VISIBLE birds
        if no birds are visible, continues to fly straight
        '''
        if not visible_birds:
            x_vel, y_vel = self.get_vel()
            return (self.x + x_vel, (self.y + y_vel))  # perhaps self.y + y_vel
        x_tot, y_tot = functools.reduce(lambda m, n: (m[0] + n[0], m[1] + n[1]), (bird_positions[i] for i in visible_birds))
        return (x_tot / len(visible_birds), y_tot / len(visible_birds))
    
    def weighted_average(self, thetas, weights):
        w = sum(weights)
        return sum(weights[i]*thetas[i] for i in range(len(weights))) / w if w else sum(thetas) // 3
    
    def angle(self, x1, y1, x2, y2):
        '''returns angle between (x1,y1) and (x2,y2)'''
        return math.atan2(-(y2 - y1), x2 - x1) * 180 / math.pi
    
    def update(self, visible_birds, too_close_birds, bird_positions, bird_velocities, too_close_to_wall, center_all_boids):
        '''
        Uses boid rules of separation, cohesion and alignment to update birds movement
        '''
        
        # If bird is too close to the wall, moving away from the wall will take priority
        if (self.x < self.x_min + self.crit_radius) or (self.y < self.y_min + self.crit_radius) or \
            (self.x > self.x_max - self.crit_radius) or (self.y > self.y_max - self.crit_radius):
            a = self.angle(self.x, self.y, self.x_mid, self.y_mid)
            thetas = [a]*3
        else:
            #follow normal bird behavior rules:
            theta_mass = theta_social_dist = theta_alignment = self.theta
            
            # fly towards the center of mass
            if self.behavior['center_of_mass']:
                #xbar, ybar = self.center_mass(visible_birds - too_close_to_wall, bird_positions)
                xbar, ybar = center_all_boids
                #xbar, ybar = self.center_mass(visible_birds, bird_positions)
                theta_mass = self.angle(self.x, self.y, xbar, ybar) % 360
            
            # keep your distance from neighboring birds
            if self.behavior['social_distancing']:
                if not too_close_birds:
                    theta_social_dist = self.theta % 360
                else:
                    behavior_thetas = []
                    for i in too_close_birds:
                        # +180 because we want to move away from visible birds
                        behavior_thetas.append(self.angle(self.x, self.y, bird_positions[i][0], bird_positions[i][1]))
                    theta_social_dist = (180 + sum(behavior_thetas) / len(behavior_thetas)) % 360
                
            # align vector with neighboring birds
            if self.behavior['alignment']:
                if not visible_birds:
                    theta_align = self.theta
                else:
                    theta_align = 0
                    for i in visible_birds:
                        theta_align += self.angle(0, 0, bird_velocities[i][0], bird_velocities[i][1])
                    theta_align = theta_align // len(visible_birds)
        
            thetas = [theta_mass, theta_social_dist, theta_alignment]
            #print()
            #print([int(t) for t in thetas])
        
        
        weights = [self.behavior['center_of_mass'], self.behavior['social_distancing'], self.behavior['alignment']]
        target_theta = self.weighted_average(thetas, weights)
        target_theta %= 360
        
        # update birds position (consider doing this after updating direction)
        x_vel, y_vel = self.get_vel()
        self.x += x_vel
        self.y += y_vel
        self.x = max(self.x_min, min(self.x, self.x_max))
        self.y = max(self.y_min, min(self.y, self.y_max))
        
        #print('curr/target',int(self.theta), int(target_theta))
        
        # update birds direction
        if abs(target_theta - self.theta) <= self.max_turn or abs(target_theta - 360 - self.theta) <= self.max_turn:
            self.theta = target_theta
        else:
            if abs(target_theta - self.theta) <= 180:
                self.theta += self.max_turn if target_theta > self.theta else -self.max_turn
            else:
                self.theta += self.max_turn if target_theta < self.theta else -self.max_turn
        self.theta %= 360
        
        #print('new_theta',int(self.theta))
        #print()
        

        

            
        
        
    
    
        
    
        
        
    
    
    
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
    