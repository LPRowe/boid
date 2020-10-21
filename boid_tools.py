# -*- coding: utf-8 -*-
"""
Created on Tue Oct 20 22:08:16 2020

@author: rowe1
"""

import pygame

class Boid(object):
    def __init__(self, x, y, theta, s):
        self.x = x
        self.y = y
        self.theta = theta
        self.s = s # speed
        
    def draw(self, surface, image):
        surface.blit(image, (self.x, self.y))
    
    