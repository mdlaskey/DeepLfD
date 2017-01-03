from scipy import signal
import numpy as np
import cv2
import IPython
from alan.rgbd.bincam_2D import BinaryCamera
from alan.p_rope_grab_R.options import Rope_GrabROptions as Options
import time

"""
parameters:
    binary image with rope in white
output:
    an (x, y) pixel coordinate for each endpoint
"""
def find_endpoints(img,arm = 'RIGHT'):
    #endpoint are characterized by fewer white pixels in nearby region
    filt = np.full((15, 15), -1, dtype = np.int)
    filt[7][7] = 100 #tuned paramter

    #convolve and round (low to zero)
     
    conv_img = signal.fftconvolve(img[:,:,0], filt, mode = "same")
    conv_img = conv_img.astype(np.int)
    conv_img = conv_img.clip(min = 0)
    
    conv_img = 255*conv_img/np.max(conv_img)
    conv_img = conv_img.astype(np.uint8)


    thresh, conv_img = cv2.threshold(conv_img,thresh = 190, maxval = 255, type=cv2.THRESH_BINARY)
    #get endpoint pixels
    
    coords = np.transpose(np.nonzero(conv_img))
 
    #put in [x, y] format
    if(coords[0][1] < coords[-1][1]):
        e1 = [coords[0][1], coords[0][0]]
        e2 = [coords[-1][1], coords[-1][0]]
    else:
        e2 = [coords[0][1], coords[0][0]]
        e1 = [coords[-1][1], coords[-1][0]]

    IPython.embed()
    #Add x-offset
    e1[1] = e1[1] + 15
    e2[1] = e2[1] + 15
    if(arm == 'RIGHT'):
        return e1
    else: 
        return e2




if __name__ == '__main__':
    options = Options()

    b = BinaryCamera(options)
    b.open(threshTolerance= Options.THRESH_TOLERANCE)
  
    while (1):
        frame = b.read_binary_frame()
        out = frame#+o
        cv2.imshow("camera", out)
        print("reading")
        a = cv2.waitKey(30)
        if a == 1048603:
            cv2.destroyWindow("camera")
            break
        time.sleep(.005)        
        
 
    img,points = find_endpoints(frame)

    print "POINTS ", points
    cv2.imshow('original',frame)
    cv2.imshow('found_points',img)

    IPython.embed()

    