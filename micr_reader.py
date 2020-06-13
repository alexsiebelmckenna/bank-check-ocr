#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 12 18:34:25 2020

@author: alexsiebelmckenna
"""

import pandas as pd
import numpy as np
import argparse
import imutils
import cv2
from skimage.segmentation import clear_border
from imutils import contours

def extract_digits_and_symbols(image, charCnts, minW=5, minH=15):
    # grab the internal Python iterator for the list of character
	# contours, then  initialize the character ROI and location
	# lists, respectively
    
    charIter = charCnts.__iter__()
    rois = []
    locs = []
    # keep looping over the character contours until we reach the end
	# of the list
    while True:
        try:
            # grab the next character contour from the list, compute
			# its bounding box, and initialize the ROI 
            c = next(charIter)
            (cX, cY, cW, cH) = cv2.boundingRect(c)
            roi = None
            
            # check to see if the width and height are sufficiently
			# large, indicating that we have found a digit
            if cW >= minW and cH >= minH:
                # extract the ROI
                roi = image[cY:cY + cH, cX:cX + cW]
                rois.append(roi)
                locs.append((cX, cY, cX + cW, cY + cH))
            # otherwise, we are examining one of the special symbols
            else:
            # MICR symbols include three separate parts, so we
			# need to grab the next two parts from our iterator,
			# followed by initializing the bounding box
			# coordinates for the symbol
                parts = [c, next(CharIter), next(CharIter)]
                (sXA, sYA, sXB, sYB) = (np.inf, np.inf, -np.inf, -np.inf)
                
                # loop over the parts
                for p in parts:
                    # compute the bounding box for the part, then
    				# update our bookkeeping variables
                    (pX, pY, pW, pH) = cv2.boundingRect(p)
                    sXA = min(sXA, pX)
                    sYA = min(xYA, pY)
                    sXB = max(sXB, pX + pW)
                    sYB = max(sYB, pY + pH)
                    
                # extract the ROI
                rois = image[sYA:sYB, sXA:sXB]
                rois.append(roi)
                locs.append((sXA, sYA, sXB, sYB))

            
            # we have reached the end of the iterator; gracefully break
            # the loop
        except StopIteration:
            break
        
    # return a tuple of the ROIs and locations
    return (rois, locs)

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True,
                help="path to input image")
ap.add_argument("-r", "--reference", required=True,
                help="path to reference MICR E-13B font")
args = vars(ap.parse_args())

# initialize the list of reference character names, in the same
# order as they appear in the reference image where the digits
# their names and:
# T = Transit (delimit bank branch routing transit #)
# U = On-us (delimit customer account number)
# A = Amount (delimit transaction amount)
# D = Dash (delimit parts of numbers, such as routing or account)

charNames = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0",
             "T", "U", "A", "D"]

# load the reference MICR image from disk, convert it to grayscale,
# and threshold it, such that the digits appear as *white* on a
# *black* background
ref = cv2.imread(args["reference"])