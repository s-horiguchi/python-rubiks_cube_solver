#!/usr/bin/env python
#-*- coding:utf-8 -*-

import cv2.cv as cv
from copy import deepcopy
import time
from cube_def import *

SRATE = 2
ROTATE_DELAY = 3.0
WHITE_S_MIN = 20
WHITE_V_MAX = 170
WHITE_THRESH = 20

MANEUVER = 0x70
CHANGE_FACE_MANEU  = ["(r)", "(f')", "(f')", "(f')", "(f')(r)", "(r)(r)"] #up, front, right, back, left, bottom

class CubeCapture(object):
    def __init__(self, without_robot=True, next_face=None):
        self.without_robot = without_robot

        self.capture = cv.CreateCameraCapture(0)
        cv.NamedWindow("cube_capture.py", 1)
        frame = cv.QueryFrame(self.capture)
        if not frame:
            raise IOError, "Couldn't find camera."
        self.W, self.H = cv.GetSize(frame)
        self.W = self.W / SRATE
        self.H = self.H / SRATE
        self.img = cv.CreateImage((self.W, self.H), 8, 3)
        self.hsv = cv.CreateImage((self.W, self.H), 8, 3)
        if self.W >= self.H:
            self.one_side = self.H / 9 * 2. # the length of one side of the sqare of one sticker
        else:
            self.one_side = self.W / 9 * 2.
        self.left_top = ((self.W-9/2*self.one_side)/2+self.one_side/4, (self.H-9/2*self.one_side)/2+self.one_side/4)
        
        self.colors_list = [None]*6
        self.fnum_list = [[[None, None, None],[None, None, None],[None, None, None]],[[None, None, None],[None, None, None],[None, None, None]],[[None, None, None],[None, None, None],[None, None, None]],[[None, None, None],[None, None, None],[None, None, None]],[[None, None, None],[None, None, None],[None, None, None]],[[None, None, None],[None, None, None],[None, None, None]]]
        self.facenum = 0
        self.colors = [[0,0,0], [0,0,0], [0,0,0]]

        self.solver = next_face
        self.counter = 0
        #print "one_side:", self.one_side
        #print "W", self.W
        #print "H", self.H
        #print "left_top:", self.left_top

    def save_color(self):
        self.colors_list[self.facenum] = deepcopy(self.colors)
        # change capturing face of the cube
        self.solver.send_command(MANEUVER, CHANGE_FACE_MANEU[self.facenum])
        self.facenum += 1
        if not self.without_robot: # re-set
            self.last_time = time.time()

        return

    def process_colors(self):
        center_colors = [self.colors_list[i][1][1] for i in [2,4,0,5,1,3]] # up,front,right,back,left,bottom
        #print center_colors[2] 
        center_colors[2] = (0, 0, 255)  # to support strange cube mark on the center of the white face of the japanese official cube
        print "center_colors:", center_colors
        for i,f in enumerate([2,4,0,5,1,3]):
            for iy in xrange(3):
                for ix in xrange(3):
                    #print "color(HSV):", self.colors_list[f][iy][ix]
                    if (f == 0 and ix == 1 and iy == 1) or ((self.colors_list[f][iy][ix][1] - WHITE_S_MIN) + (WHITE_V_MAX - self.colors_list[f][iy][ix][2]) < WHITE_THRESH):
                        #print "preferentially white"
                        self.fnum_list[i][iy][ix] = 2
                    else:
                        diff_list = [[c - hsv for c,hsv in zip(cc, self.colors_list[f][iy][ix])] for cc in center_colors]
                        #print "diff list:", diff_list
                        assert diff_list.count(min(diff_list, key=lambda x: abs(x[0]))) == 1 ##
                        self.fnum_list[i][iy][ix] = diff_list.index(min(diff_list, key=lambda x: abs(x[0])))
                    #print self.fnum_list
        return "|".join(["".join(["".join([COLOR[x] for x in y]) for y in f]) for f in self.fnum_list])

    def main(self):
        if not self.without_robot:
            self.last_time = time.time()
        print "[!!] capture white face first"
        
        while self.facenum < 6:
            if not self.without_robot and (time.time() - self.last_time > ROTATE_DELAY):
                self.save_color()
            frame = cv.QueryFrame( self.capture )
            if not frame:
                raise IOError, "Camera Error"
            
            cv.Resize(frame, self.img)
            cv.CvtColor(self.img, self.hsv, cv.CV_RGB2HSV)
            
            for iy in xrange(3):
                for ix in xrange(3):
                    lefttop = (int(self.left_top[0]+self.one_side*3/2*ix), int(self.left_top[1]+self.one_side*3/2*iy))
                    rightbottom = (int(self.left_top[0]+self.one_side*3/2*ix+self.one_side), int(self.left_top[1]+self.one_side*3/2*iy+self.one_side))
                    
                    col = cv.Avg(self.img[lefttop[1]:rightbottom[1],lefttop[0]:rightbottom[0]])
                    cv.Rectangle(self.img, lefttop, rightbottom, (0,0,0), cv.CV_FILLED)
                    cv.Rectangle(self.img, (lefttop[0]+3,lefttop[1]+3), (rightbottom[0]-3,rightbottom[1]-3), col, cv.CV_FILLED)
                    hsv_col = cv.Avg(self.hsv[lefttop[1]:rightbottom[1],lefttop[0]:rightbottom[0]])
                    #print hsv_col
                    self.colors[iy][ix] = hsv_col[:]

            cv.ShowImage("cube_capture.py", self.img)
            
            c = cv.WaitKey(10) % 0x100
            if c == 27: # ESC
                break
            elif self.without_robot and chr(c) == " ":
                self.save_color()
        #print self.colors_list
        if self.colors_list[-1]:
            r = self.process_colors()
        else:
            r = None
        cv.DestroyWindow("cube_capture.py")
        return r

if __name__ == "__main__":
    from optparse import OptionParser

    parser = OptionParser("Usage: ./%prog [options]")
    (options, args) = parser.parse_args()

    cc = CubeCapture()
    print cc.main()
