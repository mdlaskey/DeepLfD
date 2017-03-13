'''
Class to handle test and training data for the neural network

Author : Jonathan Lee

'''

from numpy.random import rand
import random
import numpy as np
import numpy.linalg as LA
import IPython
import tensorflow as tf
import cv2
import IPython
import sys

from perception import DepthImage


def process_out(n):
    '''
    Computes argmax of a numpy array

    Parameters
    ----------
    n : numpy array

    Returns 
    -------
    out: int
    '''
    out = np.argmax(n)

    return out


def im2tensor(im,channels=1):
    """
    convert 3d image (height, width, 3-channel) where values range [0,255]
    to appropriate pipeline shape and values of either 0 or 1
    cv2 --> tf

    Prameters
    ---------
    im : numpy array 
        matrix with shape of image

    channels : int
        number of channels into the network (Default 1)

    Returns
    -------
    numpy array
        image converted to the correct tensor shape
    """
    shape = np.shape(im)
    h, w = shape[0], shape[1]
    zeros = np.zeros((h, w, channels))
    for i in range(channels):
        zeros[:,:,i] = im[:,:,i]
    return zeros



def parse(filepath, stop=-1):
    """
    Parses file containing paths and labels into list
    of tupals in the form of:
    
    data =  [ 
                (path, [label1, label2 ... ])
                ...
            ]
    """
    f = open(filepath, 'r')
    tups = []
    lines = [ x for x in f ]
    random.shuffle(lines)
    for i, line in enumerate(lines):
        split = line.split(' ')
        path = split[0]
        labels = np.array( [ float(x) for x in split[1:] ] )
        tups.append((path, labels))
        if (not stop < 0) and i >= stop-1:
            break            
    return tups

class IMData():
    
    def __init__(self, trajectories,channels=1):
        '''
        lists of trajectories each with images and labels 
        '''
        self.train_trajs = []
        self.test_trajs = []
        num_t = len(trajectories)

        num_test_trajs = max(int(0.1 * num_t), 1)
        is_train_inds = [True] * num_t
        is_train_inds[:num_test_trajs] = [False] * num_test_trajs
        random.shuffle(is_train_inds)

        for i, is_train in enumerate(is_train_inds):
            if is_train:
                self.train_trajs.append(trajectories[i])
            else:
                self.test_trajs.append(trajectories[i])

        self.i = 0
        self.channels = channels

    def next_train_batch(self, n):
        """
        Read into memory on request
        :param n: number of examples to return in batch
        :return: tuple with images in [0] and labels in [1]
        """ 
        if self.i + n > len(self.train_trajs):
            self.i = 0
            random.shuffle(self.train_trajs)

        batch_traj = self.train_trajs[self.i:n+self.i]
        
        batch = []
        for traj in batch_traj:
            for state, labels in traj:    

                im = im2tensor(state,self.channels)
           
            
                batch.append((im, labels))  
            #print path            

        #IPython.embed()
        batch = zip(*batch)
        self.i = self.i + n
       
        return list(batch[0]), list(batch[1])


    def next_test_batch(self):
        """
        read into memory on request
        :return: tuple with images in [0], labels in [1]
        """
        batch = []
        for traj in self.test_trajs:
            for state,label in traj:
      
                im = im2tensor(state,self.channels)
           
                batch.append((im, label))  
                #print path          

  
        random.shuffle(self.test_trajs)
        batch = zip(*batch)
        return list(batch[0]), list(batch[1])
