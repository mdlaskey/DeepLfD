import pygame
import numpy as np
import time
import sys

class XboxController:
    def __init__(self, scale=0.5):
        pygame.init()
        pygame.joystick.init()
        self.controller = pygame.joystick.Joystick(0)
        self.controller.init()
        
        self.trigger_l = Trigger(self.controller.get_axis(2))
        self.trigger_r = Trigger(self.controller.get_axis(5))

        self.driftLimit = .05
        self.scale = scale

        #self.calibrate()
        
    def getUpdates(self):
        for event in pygame.event.get(): # User did something
            # start pressed
            if event.type == pygame.JOYBUTTONDOWN and self.controller.get_button(7) == 1.0: # If user clicked close
                return None
            #elif self.controller.get_button(3) == 1.0:
            #    return 'switch'
                # Flag that we are done so we exit this loop
                
        state = self.getControllerState() 
        result = [state['trigger_l'], state['trigger_r'], self.controller.get_button(0), self.controller.get_button(1),
                    self.controller.get_button(2), self.controller.get_button(3)]
        return result


    def getUpdate(self):
        pygame.event.clear()
        while True:
            event = pygame.event.wait() # User did something
        
            # start pressed
            if event.type == pygame.JOYBUTTONDOWN and self.controller.get_button(7) == 1.0: # If user clicked close
                return None
            #elif self.controller.get_button(3) == 1.0:
            #    return 'switch'
                # Flag that we are done so we exit this loop
                
            state = self.getControllerState() 
            result = [state['trigger_l'], state['trigger_r'], self.controller.get_button(0), self.controller.get_button(1),
                        self.controller.get_button(2), self.controller.get_button(3)]
            return result
        
    def calibrate(self):
        save_stdout = sys.stdout
        sys.stdout = open('trash', 'w') 
        # calibrate sticks 
        # reset offsets and scaling factors 
        length = len(self.offsets)
        self.offsets = np.zeros(length)
        self.uScale = np.ones(length)
        self.lScale = np.ones(length)
        
        state = self.getControllerState()      
        self.offsets = self.convert(state)    
        self.uScale = abs(1/(np.ones(length)-self.offsets))
        self.lScale = abs(1/(-np.ones(length)-self.offsets))
        sys.stdout = save_stdout
        

    def getControllerState(self):
        pygame.event.clear()
        self.update()
        #if self.isInUse():
        state = {'trigger_l':self.trigger_l.getPos(), 'trigger_r':self.trigger_r.getPos()}
        return state
            
    def update(self):
        self.trigger_l.setCurrent(self.controller.get_axis(2))
        self.trigger_r.setCurrent(self.controller.get_axis(5))


class Trigger:
    def __init__(self, axis0):
        self.initA0 = axis0
        self.a0 = self.initA0

    def getPos(self):
        return self.a0

    def setCurrent(self, a0):
        if a0 > 0.5:
            self.a0 = 1
        else:
            self.a0 = 0
        return self.getPos()

    def isInUse(self):
        return self.a0!=self.initA0
