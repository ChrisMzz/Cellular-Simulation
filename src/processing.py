from colorsys import hls_to_rgb
from colorsys import rgb_to_hls
import numpy as np


class State:
    def __init__(self, name, turns, **kwargs):
        self.name = name
        self.turns = turns
        args = {}
        for arg, value in kwargs.items():
            args[arg] = value
        self.args = args
        
    def __eq__(self, other): # to facilitate state localisation
        if type(other) == State:
            return self.name == other.name
        else:
            return self.name == other
        
    def __getitem__(self, item):
        return self.args[item]
    



# state management, position management ---------------------------------------

def update_old_states(p, states):
    old_states = []
    for state in states[p]:
        if state.turns > 1:
            state.turns -= 1
            old_states.append(state)
    return old_states


def get_current_adjacents(p):
    adjacents = []
    if p%690 != 0:
        adjacents.append(p-1)
    if p%690 != 689:
        adjacents.append(p+1)
    if p//690 != 0:
        adjacents.append(p-690)
    if p//690 != 514:
        adjacents.append(p+690)
    return adjacents

# --------------------------------------------------------------------------------




def gridify(p, pixel, current_bp, adjacents, states): # test process / doesn't do anything interesting
    old_states = update_old_states(p, states)
    if sum(pixel) <= sum(current_bp):
        return tuple(current_bp), old_states
    elif max(pixel) <= max(current_bp):
        temp_pixel = [255-pixel[0],255-pixel[1],255-pixel[2]]
        temp_pixel[list(pixel).index(max(pixel))] = 0
        return tuple(temp_pixel), old_states
    else:
        return (255-pixel[0],255-pixel[1],255-pixel[2]), old_states


# widen

def widen(p, pixel, current_bp, adjacents, states):
    old_states = update_old_states(p, states)
    temp = [sum(adj) for adj in adjacents]
    return adjacents[temp.index(max(temp))], old_states

def inverse_widen(p, pixel, current_bp, adjacents, states):
    old_states = update_old_states(p, states)
    temp = [sum(adj) for adj in adjacents]
    return adjacents[temp.index(min(temp))], old_states

def optim_widen(p, pixel, current_bp, adjacents, states):
    old_states = update_old_states(p, states)
    temp = [sum(adj) for adj in adjacents]
    if sum(temp)/len(temp) < 400:
        return adjacents[temp.index(max(temp))], old_states + [State("widened",1)]
    else:
        return adjacents[temp.index(min(temp))], old_states + [State("shrunk",1)]


# lum

def brighten(p, pixel, current_bp, adjacents, states):
    old_states = update_old_states(p, states)
    temp = rgb_to_hls(pixel[0]/255, pixel[1]/255, pixel[2]/255)
    if min([sum(adj) for adj in adjacents]) < 400 and sum(pixel) < 500:
        temp = hls_to_rgb(temp[0],1-temp[1], temp[2])
        return (int(temp[0]*255), int(temp[1]*255), int(temp[2]*255)), old_states
    else:
        temp = hls_to_rgb(temp[0],0.5+temp[1]/2, temp[2])
        return (int(temp[0]*255), int(temp[1]*255), int(temp[2]*255)), old_states


# rotation - conserves states

def rotate(p, pixel, current_bp, adjacents, states):
    old_states = update_old_states(p, states)
    new_states = []
    for state in states[p]:
        new_states.append(state)
    if "rotated" in new_states:
        i = new_states.index("rotated")
        theta = new_states[i]["angle"]
        new_states.pop(i)
    else:
        theta = 0
    temp = rgb_to_hls(pixel[0]/255, pixel[1]/255, pixel[2]/255)
    temp = hls_to_rgb(((temp[0]*360+45)%360)/360,temp[1],temp[2])
    return (int(temp[0]*255), int(temp[1]*255), int(temp[2]*255)), new_states + old_states + [State("rotated", 1, angle=theta+45)]

def rotate_with_momentum(p, pixel, current_bp, adjacents, states):
    old_states = update_old_states(p, states)
    new_states = []
    for state in states[p]:
        new_states.append(state)
    if "rotated" in new_states:
        i = new_states.index("rotated")
        theta = new_states[i]["angle"]
        new_states.pop(i)
    else:
        theta = 0
    temp = rgb_to_hls(pixel[0]/255, pixel[1]/255, pixel[2]/255)
    adj_luminosity = sum(current_bp)//8
    temp = hls_to_rgb(((temp[0]*360+adj_luminosity)%360)/360,temp[1],temp[2])
    return (int(temp[0]*255), int(temp[1]*255), int(temp[2]*255)), old_states + [State("rotated", 1, angle=theta+adj_luminosity)]


# map morphs - breaks momentum, recursive

def annihilate(p, pixel, current_bp, adjacents, states):
    if min([max(adj) for adj in adjacents]) > 150 and min([sum(adj) for adj in adjacents]) > 50 and max([sum(adj) for adj in adjacents]) < 500:
        return (int(3*pixel[0]/4),int(3*pixel[1]/4),int(3*pixel[2]/4)), [State("annihilated",1)]
    elif "annihilated" in states[p]:
        return (int(2*pixel[0]/3),int(2*pixel[1]/3),int(2*pixel[2]/3)), [State("annihilated",1)]
    else:
        return pixel, []
    
def progressive_annihilate(p, pixel, current_bp, adjacents, states):
    near_annihilation = False
    for pos in get_current_adjacents(p):
        if "annihilated" in states[pos]:
            near_annihilation = True
    if min([max(adj) for adj in adjacents]) > 220 and min([sum(adj) for adj in adjacents]) > 50 and max([sum(adj) for adj in adjacents]) < 500:
        return (int(3*pixel[0]/4),int(3*pixel[1]/4),int(3*pixel[2]/4)), [State("annihilated",1)]
    elif "annihilated" in states[p] or near_annihilation or np.random.randint(0,16)==0:
        return (int(pixel[0]/2),int(pixel[1]/2),int(pixel[2]/2)), [State("annihilated",1)]
    else:
        return pixel, []

def trail(p, pixel, current_bp, adjacents, states):
    unsorted = [sum(adj) for adj in adjacents]
    temp = sorted([sum(adj) for adj in adjacents])
    if len(temp) < 3:
        return pixel, []
    if sum(temp[:2]) < 600 or "trail" in states[p]:
        pix0 = adjacents[unsorted.index(temp[-1])]
        pix1 = adjacents[unsorted.index(temp[-2])]
        return (int((pix0[0]+pix1[0])/2),int((pix0[1]+pix1[1])/2),int((pix0[2]+pix1[2])/2)), [State("trail",1)]
    else:
        return (int(pixel[0]/2),int(pixel[1]/2),int(pixel[2]/2)), [State("annihilated",1)]
        


# move

def left(p, pixel, current_bp, adjacents, states):
    old_states = update_old_states(p, states)
    if p%690 == 0:
        return pixel, old_states
    else:
        return adjacents[get_current_adjacents(p).index(p-1)], old_states

def right(p, pixel, current_bp, adjacents, states):
    old_states = update_old_states(p, states)
    if p%690 == 689:
        return pixel, old_states
    else:
        return adjacents[get_current_adjacents(p).index(p+1)], old_states
    
def up(p, pixel, current_bp, adjacents, states):
    old_states = update_old_states(p, states)
    if p//690 == 0:
        return pixel, old_states
    else:
        return adjacents[get_current_adjacents(p).index(p-690)], old_states

def down(p, pixel, current_bp, adjacents, states):
    old_states = update_old_states(p, states)
    if p//690 == 514:
        return pixel, old_states
    else:
        return adjacents[get_current_adjacents(p).index(p+690)], old_states


def move_random(p, pixel, current_bp, adjacents, states):
    old_states = update_old_states(p, states)
    return adjacents[np.random.randint(0,len(get_current_adjacents(p)))], old_states

def hyperactive(p, pixel, current_bp, adjacents, states):
    old_states = update_old_states(p, states)
    thresh = len(states[p])
    if thresh == 0:
        return pixel, old_states
    test = np.random.randint(0,thresh)
    if test > 0:
        return adjacents[np.random.randint(0,len(get_current_adjacents(p)))], old_states
    else:
        return pixel, old_states

def cell_active(p, pixel, current_bp, adjacents, states):
    old_states = update_old_states(p, states)
    if sum(current_bp) > 450:
        thresh = len(states[p]) + sum([len(states[pos]) for pos in get_current_adjacents(p)])
        if thresh == 0:
            return pixel, old_states
        test = np.random.randint(0,thresh)
        if test > 0:
            return adjacents[np.random.randint(0,len(get_current_adjacents(p)))], old_states
    return pixel, old_states
            


# color morphs


def hue_influence(p, pixel, current_bp, adjacents, states):
    old_states = update_old_states(p, states)
    hls = [rgb_to_hls(a[0]/255, a[1]/255, a[2]/255)[2] for a in adjacents]
    i = hls.index(max(hls))
    colorful = adjacents[i]
    hue = int(rgb_to_hls(colorful[0]/255, colorful[1]/255, colorful[2]/255)[0]*360)
    temp = rgb_to_hls(pixel[0]/255, pixel[1]/255, pixel[2]/255)
    temp = hls_to_rgb((((temp[0]*360+hue)//2)%360)/360,temp[1],(max(hls)+temp[2])/2)
    return (int(temp[0]*255), int(temp[1]*255), int(temp[2]*255)), old_states + [State("rotated", 1, angle=((temp[0]*360+hue)//2)%360)]






# chaos

def chaos(p, pixel, current_bp, adjacents, states):
    actions = [gridify, widen, inverse_widen, optim_widen, brighten, \
            rotate, rotate_with_momentum, annihilate, progressive_annihilate, trail, \
            left, right, up, down, move_random, hyperactive, cell_active, hue_influence]
    n = np.random.randint(0,len(actions))
    return actions[n](p, pixel, current_bp, adjacents, states)




