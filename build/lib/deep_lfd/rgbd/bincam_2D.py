"""
Webcam class for generating binary masked images. 
Class connects to webcam and computes a background subtraction 

Author: Michael Laskey
"""
import cv2
import numpy as np
import datetime
import os
import IPython

from bgSegmentation import segmentBG, bgBoundsByMode
from basic_imaging import add_dim, deNoise
import scipy.ndimage.morphology as snm

class BinaryCamera():

    def __init__(self, options=None):
        """
        initialization class
        
        Parameters
        ----------

        options : 
            An instance of the Option Class, which is used to specify 
            the dimensions and location of the image 
        """
        self.vc = None
        self.Options = options


        self.lowerBound = -1
        self.upperBound = -1


    """ idNum usually 0, 1, 2, 3"""
    def open(self, idNum = 0, threshTolerance = 40):
        """
        Used to Open the webcam and cacultate the background subtraction
        
        Parameters
        ----------

        idnum : 
        The idNum of the USB port for the webcam, if known. Default is to search until
        a webcam is found on the port. 

        threshTolerance : 
        The tolerance of the binary mask, higher values incresea the amount of information removed
        Default value is 40

        """

        for idNum in range(idNum,100):
            self.vc = cv2.VideoCapture(idNum)
            print idNum
            for i in range(10):
                self.vc.read()
            r, f = self.vc.read()
            if(not f == None):
                break
  
        if(f == None): 
            raise Exception('Web Cam is Not Connected')
 
        #for more saturated version, set saturation to .35
        self.vc.set(cv2.cv.CV_CAP_PROP_SATURATION ,0.15)
        self.vc.set(cv2.cv.CV_CAP_PROP_CONTRAST ,0.12)
        self.vc.set(cv2.cv.CV_CAP_PROP_BRIGHTNESS ,0.5)

        for i in range(10):
            sampleImg = self.read_frame()

        #############HARD CODING CONSTANTS VERY DANGEROUS###########
        self.lowerBound = np.array([ 14, 143,  77]) 
        self.upperBound = np.array([114, 243, 177])
        
  
    def close(self):
        """
        Relases the webcam, if the camera is opened
        
        """
        if self.is_open():
            self.vc.release()

    def is_open(self):
        """
        Checks if the camera is opened
        
        """
        return self.vc is not None and self.vc.isOpened()

    def read_raw(self):
        """
        Reads a raw frame from the webcamera. 

        Returns 
        -------
        numpy array
            WxHx3 matrix that corresponds to the image. W and H are specfied by camera model
        """
        if(not self.is_open()): 
            raise Exception('Web Cam is Not Opened')

        rval, frame = self.vc.read()

        return frame

    def read_frame(self):
        """
        Reads an image that has the dimensions and location specified in the options file

        Returns
        -------
        numpy array
            WxHx3 matrix that corresponds to the image. W and H are speficied by Options file


        
        """
        frame = self.read_raw()

        if not self.Options == None:
            frame = frame[0+self.Options.OFFSET_Y:self.Options.HEIGHT+self.Options.OFFSET_Y, 0+self.Options.OFFSET_X:self.Options.WIDTH+self.Options.OFFSET_X]

        return frame

    def read_frame_options(self,Options):
        """
        Reads an image that has the dimensions and location specified in the options file
        Allows the user to specify a different options file

        Parameters
        ----------
        Options: 
            An instance of the Option Class, which is used to specify 
            the dimensions and location of the image 
        Returns
        -------
        numpy array
            WxHx3 matrix that corresponds to the image. W and H are speficied by Options file

        """
        frame = self.read_raw()

        frame = frame[0+Options.OFFSET_Y:Options.HEIGHT+Options.OFFSET_Y, 0+Options.OFFSET_X:Options.WIDTH+Options.OFFSET_X]

        return frame



    def display_frame(self):
        """
        Displays the color framed specifed by the internal options file 

        """
        frame = self.read_frame()
        
        cv2.imshow("preview", frame)
        cv2.waitKey(30)
        return frame

    def color_to_binary(self,img):
        """
        Converts a color image to a binary image

        Parameters
        ----------
        img: numpy array
            WxHx3 matrix that represents an RGB image

        Returns
        -------
        img 
            WxHx1 matrix that has been segmented 

        """
       

        img = self.apply_mask(img)
        img = self.filter_binary_image(img)
        return add_dim(img)

    def filter_binary_image(self,img):
        """
        Applies a filter to fill in small holes in the image

        Parameters
        ----------
        img: numpy array
            WxH matrix that is boolean in value

        Returns
        -------
        numpy array 
            WxH matrix that has the wholes filled in 



        """
        #img = snm.grey_closing(img,size=(10,10))
        return img

    def apply_mask(self, img):
        """
        Applies the segementation mask 

        Parameters
        ----------
        img: numpy array
            WxHx3 matrix that represents an RGB image

        Returns
        -------
        numpy array 
            WxH matrix that has been segmented 



        """
        if(not self.is_open()): 
            raise Exception('Web Cam is Not Opened')

        img = segmentBG(img, self.lowerBound, self.upperBound)
        return img

    def read_single_channel_binary(self):
        """
        Not supported

        """
        frame = self.read_frame()
        return frame, self.apply_mask(frame)


    def read_gray_frame(self):
        """
        reads a grayscale image from the webcam, with location and dimensions
        specified by options file


        Returns
        -------
        numpy array 
            WxHx1 matrix that is a grayscale image

        """
        frame = self.read_frame()
        return cv2.cvtColor( frame, cv2.COLOR_RGB2GRAY )

    def read_color_frame(self):
        """
        reads a color image from the webcam, with location and dimensions
        specified by options file


        Returns
        -------
        numpy array 
            WxHx3 matrix that is a colored image

        """
        return self.read_frame()

    def read_binary_frame(self,options = None):
        """
        reads a binary image from the webcam, with location and dimensions
        specified by options file

        Parameters
        ----------

        options: 
            An instance of the Option Class, which is used to specify 
            the dimensions and location of the image 
            (Default is the internal options class)


        Returns
        -------
        numpy array 
            WxHx1 matrix that is a binary image

        """
        if(not options == None ):
            frame = self.read_frame_options(options)
        else:
            frame = self.read_frame()

        frame = self.apply_mask(frame)
        frame = self.filter_binary_image(frame)
        return add_dim(frame)

    

    


if __name__ == "__main__":
    bincam = BinaryCamera()
    bincam.open(threshTolerance= 80)

    frame = bincam.read_raw()


    while (1):
        # frame = bincam.display_frame()

        # out = frame + o
        # cv2.imshow("camera", out)
        # print("reading")
        a = cv2.waitKey(30)
        if a == 1048603:
            cv2.destroyWindow("camera")
            break

        frame = bincam.read_raw()
        cv2.imshow("cam", frame)
        cv2.waitKey(30)

    #bincam.release()
