'''
Class to handle test and training data for the neural network

Author : Jonathan Lee

'''

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
    
    def __init__(self, train_path, test_path,channels=1):


        self.train_tups = parse(train_path)
        self.test_tups = parse(test_path)

        self.i = 0
        self.channels = channels

        random.shuffle(self.train_tups)
        random.shuffle(self.test_tups)

    def next_train_batch(self, n):
        """
        Read into memory on request
        :param n: number of examples to return in batch
        :return: tuple with images in [0] and labels in [1]
        """
        if self.i + n > len(self.train_tups):
            self.i = 0
            random.shuffle(self.train_tups)
        batch_tups = self.train_tups[self.i:n+self.i]
        batch = []
        for path, labels in batch_tups:
            im = DepthImage.open(path)
           
            
            if(im == None):
                raise Exception('Image ' + path +' Not Found')
            im = im2tensor(im,self.channels)
           
            
            batch.append((im, labels))  
                #print path            

            
        batch = zip(*batch)
        self.i = self.i + n
        return list(batch[0]), list(batch[1])


    def next_test_batch(self):
        """
        read into memory on request
        :return: tuple with images in [0], labels in [1]
        """
        batch = []
        for path, labels in self.test_tups[:200]:
            im = DepthImage.open(path)
            
            if(im == None):
                raise Exception('Image ' + path +' Not Found')
            im = im2tensor(im,self.channels)
           
            if(labels[0] > -0.99):
                batch.append((im, labels))  
                #print path          

  
        random.shuffle(self.test_tups)
        batch = zip(*batch)
        return list(batch[0]), list(batch[1])
