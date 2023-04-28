from processing import *
import numpy as np


class Process:
    def __init__(self, preset_name="Default", *args):
        
        
        temp = [gridify, widen, inverse_widen, optim_widen, brighten, \
            rotate, rotate_with_momentum, annihilate, progressive_annihilate, trail, \
            left, right, up, down, move_random, hyperactive, cell_active, hue_influence]
        
        # not including gridify cause it's too chaotic
        self.actions = [widen, inverse_widen, optim_widen, \
            rotate, rotate_with_momentum, annihilate, progressive_annihilate, trail, \
            hyperactive, cell_active, hue_influence, chaos, self.weighted_chaos(np.random.randint(0,10,len(temp)))]
        
        if preset_name == "Clockwork":
            self.processes = [rotate_with_momentum]*4 + [optim_widen]*2 + [rotate]*2 + [optim_widen]*4 + [widen]*2 + [inverse_widen]*2
        if preset_name == "Trails":
            self.processes = [optim_widen]*4 + [annihilate]*2 + [progressive_annihilate]*4 + [rotate_with_momentum]*2 + [widen]*2 + [progressive_annihilate]*4 + [trail]*8
        if preset_name == "Random":
            N = np.random.randint(16,64)
            processes = []
            for _ in range(N):
                processes += [self.actions[np.random.randint(0,len(self.actions))]]
            self.processes = processes
        else:
            self.processes = [widen]
        if preset_name == "Continuous Random":
            N = np.random.randint(16,64)
            processes = []
            for _ in range(N):
                processes += [self.actions[np.random.randint(0,len(self.actions))]]*np.random.randint(2,7)
            self.processes = processes[-8-args[0]:] + 4*[progressive_annihilate] + 4*[widen]
        else:
            self.processes = [widen]
            
    def __call__(self, p, pixel, current_bp, step, adjacents, states):
        return self.processes[step%len(self)](p, pixel, current_bp, adjacents, states)
        
    def __len__(self):
        return len(self.processes)
    
    def __str__(self):
        return str([action.__name__ for action in self.processes])
    
    def weighted_chaos(self, weights):
        temp = [gridify, widen, inverse_widen, optim_widen, brighten, \
            rotate, rotate_with_momentum, annihilate, progressive_annihilate, trail, \
            left, right, up, down, move_random, hyperactive, cell_active, hue_influence]
        actions = []
        for a in range(len(temp)):
            actions += [temp[a]]*weights[a]
        n = np.random.randint(0,len(actions))
        return lambda p, pixel, current_bp, adjacents, states : actions[n](p, pixel, current_bp, adjacents, states)

