#!/usr/bin/env jython
#-*- coding:utf-8 -*-

from cube import *
from cube_def import *
import datetime
from org.kociemba.twophase import *


MODES = {
    "NORMAL":[], # without restriction of notations
    "ROBOT":["U", "U'", "U2", "D", "D'", "D2", "E", "E'", "E2", "(u)", "(u')"], # cannot run these
}
MAX_DEPTH = 20
TIME_OUT = 1
## U = (r)B(r')
## D = (r)F(r')

class Solver(object):
    def __init__(self, debug=True, str_position=None, colors=None, mode="NORMAL"):
        self.cube = Cube(debug=debug, str_position=str_position, colors=colors)
        self.debug = debug
        self.mode = mode

    def format_notations(self, notations):
        formatted = ""
        if self.mode == "ROBOT":
            counter = 0
            while counter < len(notations):
                if not notations[counter] in MODES[self.mode]:
                    formatted += notations[counter]
                    counter += 1

    def run_twophase(self):
        start_time = datetime.datetime.now()
        self.cube.show_faces()

        r = Search.solution(self.cube.facelets(), MAX_DEPTH, TIME_OUT, False)
        if r == "Error 1":
            print "Error 1: There is not exactly one facelet of each colour"
        elif r == "Error 2":
            print "Error 2: Not all 12 edges exist exactly once"
        elif r == "Error 3":
            print "Error 3: Flip error: One edge has to be flipped"
        elif r == "Error 4":
            print "Error 4: Not all corners exist exactly once"
        elif r == "Error 5":
            print "Error 5: Twist error: One corner has to be twisted"
        elif r == "Error 6":
            print "Error 6: Parity error: Two corners or two edges have to be exchanged"
        elif r == "Error 7":
            print "Error 7: No solution exists for the given maxDepth"
        elif r == "Error 8":
            print "Error 8: Timeout, no solution within given time"
        else:
            print "Solution found!!"
            if self.mode != "NORMAL":
                r = self.format_with_mode(r)
            print "=>", r
        delta = datetime.datetime.now() - start_time
        print "[*] Running time: %ddays %dh:%dm:%d.%ds" % (delta.days, delta.seconds / 3600, (delta.seconds % 3600) / 60, (delta.seconds % 3600) % 60, delta.microseconds)
        print 

        return r
    

if __name__ == "__main__":
    from optparse import OptionParser

    parser = OptionParser("Usage: ./%prog [options] FACE_VIEWS")
    parser.add_option("-s", "--scramble", dest="scramble",
                      action="store_true", default=False,
                      help="scramble before solve (ignore FACE_VIEWS)")
    parser.add_option("-d", "--debug", dest="debug",
                      action="store_true", default=False,
                      help="enable debug mode")
    parser.add_option("-m", "--mode", dest="mode", metavar="MODE",
                      action="store", type="string", default="NORMAL",
                      help="specify move-notations mode[NORMAL, ROBOT] (default is NORMAL)")
    (options, args) = parser.parse_args()

    if len(args) > 0:
        if options.mode in MODES:
            s = Solver(colors=args[0], debug=options.debug, mode=options.mode)
            s.run_twophase()
        else:
            parser.print_help()
    else: # there's no FACE_VIEW
        if options.scramble:
            s = Solver(debug=options.debug, mode=options.mode)
            s.cube.scramble()
            s.run_twophase()
        else:
            parser.print_help()
