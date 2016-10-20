#!/usr/bin/env python

#The MIT License (MIT)
#Copyright (c) 2016 Massimiliano Patacchiola
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF 
#MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY 
#CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE 
#SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import numpy as np
import cv2
import sys


class RangeSkinDetector:
    """Using this detector it is possible to isolate skin color in a specified range.

    In this detector the frame given as input is filtered and the pixel which
    fall in a specific range are taken, the other rejected. Some erosion and
    dilatation operation are used in order to remove noise.
    This class use the HSV (Hue, Saturation, Value) color representation to filter pixels.
    The H and S components characterize the color (independent of illumination) 
    and V compoenent specifies the illuminations.
    """

    def __init__(self, min_range = None, max_range = None):
        """Init the face detector object.

        The skin in channel H is characterized by values between 0 and 50, 
        in the channel S from 0.23 to 0.68 (Asian and Caucasian).
        @param range_min the minimum HSV value to use as filer (numpy.array)
        @param range_max the maximum HSV value to use as filter (numpy.array)
        """
        if(min_range==None): min_range = np.array([0, 48, 80], dtype = "uint8")
        if(max_range==None): max_range = np.array([20, 255, 255], dtype = "uint8")
        # min and max range to use as filter for the detector (HSV)
        self.min_range = min_range
        self.max_range = max_range

    def setRange(self, range_min, range_max):
        """Set the min and max range used in the range detector
 
        The skin in channel H is characterized by values between 0 and 50, 
        in the channel S from 0.23 to 0.68 (Asian and Caucasian).
        @param range_min the minimum HSV value to use as filer
        @param range_max the maximum HSV value to use as filter
        """
        # min and max range to use as filter for the detector (HSV)
        self.min_range = min_range
        self.max_range = max_range

    def getRange(self):
        """Return the min and max range used in the skin detector
 
        """
        return (self.min_range, self.max_range)


    def returnFiltered(self, frame):
        """Given an input frame return the filtered version.
 
        @param frame the original frame (color)
        """
        #Convert to HSV and eliminate pixels outside the range
        frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        frame_filtered = cv2.inRange(frame_hsv, self.min_range, self.max_range)
        #Bitwise mask
	frame_filtered = cv2.bitwise_and(frame, frame, mask = frame_filtered)
        return frame_filtered

    def returnRawFiltered(self, frame):
        """Given an input frame return the Raw filtered version.
 
        This version of the function does not use the blur and bitwise 
        operations, then the resulting frame contains white pixels
        in correspondance of the skin found during the searching process.
        @param frame the original frame (color)
        """
        #Convert to HSV and eliminate pixels outside the range
        frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        frame_filtered = cv2.inRange(frame_hsv, self.min_range, self.max_range)
        return frame_filtered


    def returnFilteredDenoised(self, frame):
        """Given an input frame return the filtered and denoised version.
 
        @param frame the original frame (color)
        """
        #Convert to HSV and eliminate pixels outside the range
        frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        frame_filtered = cv2.inRange(frame_hsv, self.min_range, self.max_range)
        #Applying some denoising operation on the frame
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11))
	frame_filtered = cv2.erode(frame_filtered, kernel, iterations = 2)
	frame_filtered = cv2.dilate(frame_filtered, kernel, iterations = 2)
        #Blur and then bitwise mask
	frame_filtered = cv2.GaussianBlur(frame_filtered, (3, 3), 0)
	frame_denoised = cv2.bitwise_and(frame, frame, mask = frame_filtered)
        return frame_denoised







