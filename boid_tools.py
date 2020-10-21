# -*- coding: utf-8 -*-
"""
Created on Tue Oct 20 22:08:16 2020

@author: rowe1
"""

import pygame
import math
import functools

class Boid_Cloud(object):
    def __init__(self, wall = (0, 0, 100, 100)):
        '''
        Store single instant data for all boids
        Helpful for tweaking single boids based on other boid's behavior without
        having adverse behavior caused by the order in which boids are updated
        '''
        self.positions = []
        self.velocities = []
        self.too_close_to_wall = set()
        self.x_min, self.y_min, self.x_max, self.y_max = wall
        self.crit_radius = 100
    
    def update(self, boid_list):
        for i, bird in enumerate(boid_list):
            x, y = bird.x, bird.y
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
                    theta_bird = theta_bird if theta_bird >= 0 else theta_bird + 360
                    if (theta_low <= theta_bird <= theta_high) or (theta_low <= theta_bird % 360 <= theta_high):
                        visible.add(i)
                        if R < crit_radius:
                            too_close.add(i)
        return visible, too_close
    
    
class Boid(object):
    def __init__(self, x, y, theta, s, radius = 100, phi = 150, walls = (0, 0, 100, 100)):
        # Position / velocity params
        self.x = x
        self.y = y
        self.theta = theta
        self.s = s # speed
        
        # vision params
        self.radius = radius # can see all birds within self.radius pixel radius
        self.phi = phi # cannot see birds in the 60 degree window behind it
        
        # control params: what does the bird consider when updating it's movement
        self.behavior = {'center_of_mass': 0.25,    # steer towards the center of mass of neighbors (weight 0 .. 1)
                         'social_distancing': 1, # don't get too close to neighbors (weight 0 .. 1)
                         'alignment': 0}         # match neighbor's velocity vector (weight 0 .. 1)
        
        # turning and velocity change capabilities
        self.max_turn = 180 # cannot change more than 10 degrees in 1 frame
        self.max_acceleration = 0.2 # cannot change speed by more than 20% in 1 frame
        
        # bounds boid should not cross
        self.x_min, self.y_min, self.x_max, self.y_max = walls
        self.y_mid = (self.y_min + self.y_max) // 2
        self.x_mid = (self.x_min + self.x_max) // 2
        self.crit_radius = 0.5 * radius # the point at which birds repel from one another
        
    def draw(self, surface, image):
        surface.blit(image, (self.x, self.y))
    
    def get_vel(self):
        '''
        Returns current (x_vel, y_vel) for boid
        '''
        #theta = (self.theta - 90) % 360 # because self.theta is wrt y- axis
        theta = self.theta
        x_vel = self.s * math.cos(theta * math.pi / 180)
        y_vel = -1 * self.s * math.sin(theta * math.pi / 180) # remember down is positive for y
        return (x_vel, y_vel)
    
    def center_mass(self, visible_birds, bird_positions):
        '''
        returns the center of mass of all of the visible birds
        if no birds are visible, continues to fly straight
        '''
        if not visible_birds:
            x_vel, y_vel = self.get_vel()
            return (self.x + x_vel, self.y + y_vel)
        x_tot, y_tot = functools.reduce(lambda m, n: (m[0] + n[0], m[1] + n[1]), (bird_positions[i] for i in visible_birds))
        return (x_tot / len(visible_birds), y_tot / len(visible_birds))
    
    def weighted_average(self, thetas, weights):
        return sum(weights[i]*thetas[i] for i in range(len(weights))) / sum(weights)
    
    def angle(self, x1, y1, x2, y2):
        '''returns angle between (x1,y1) and (x2,y2)'''
        a = math.atan2(y2 - y1, x2 - x1) * 180 / math.pi
        return a if a >= 0 else a + 360
    
    def update(self, visible_birds, too_close_birds, bird_positions, bird_velocities, too_close_to_wall):
        
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
                xbar, ybar = self.center_mass(visible_birds - too_close_to_wall, bird_positions)
                theta_mass = self.angle(self.x, self.y, xbar, ybar)
                theta_mass = theta_mass if theta_mass >= 0 else theta_mass + 360
            
            # keep your distance from neighboring birds
            if self.behavior['social_distancing']:
                if not too_close_birds:
                    theta_social_dist = self.theta
                else:
                    thetas = []
                    for i in too_close_birds:
                        # +180 because we want to move away from visible birds
                        thetas.append((180 + self.angle(self.x, self.y, bird_positions[i][0], bird_positions[i][1])) % 360)
                    theta_social_dist = (sum(thetas) / len(thetas)) % 360
                
            # align vector with neighboring birds
            if self.behavior['alignment']:
                pass
        
            thetas = [theta_mass, theta_social_dist, theta_alignment]
            
        weights = [self.behavior['center_of_mass'], self.behavior['social_distancing'], self.behavior['alignment']]
        target_theta = self.weighted_average(thetas, weights)
        
        # update birds direction
        if abs(target_theta - self.theta) <= self.max_turn:
            self.theta = target_theta
        else:
            t1, t2 = self.theta - self.max_turn, self.theta + self.max_turn
            self.theta = min(t1, t2, key = lambda t: abs(target_theta - t))
        
        # update birds position
        x_vel, y_vel = self.get_vel()
        self.x += x_vel
        self.y += y_vel
        self.x = max(self.x_min, min(self.x, self.x_max))
        self.y = max(self.y_min, min(self.y, self.y_max))
        

        

            
        
        
    
    
        
    
        
        
    
    
    
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
    