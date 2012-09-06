#!/usr/bin/env jython
#-*- coding:utf-8 -*-

from cube import *
from cube_def import *
import datetime
import os
import sys
from subprocess import Popen, PIPE
from org.kociemba.twophase import *


MODES = {
    "NORMAL":[], # without restriction of notations
    "ROBOT":["U", "U'", "U2", "D", "D'", "D2", "E", "E'", "E2", "(u)", "(u')"], # cannot run these
}
MAX_DEPTH = 20
TIME_OUT = 5

class Solver(object):
    def __init__(self, debug=True, str_position=None, colors=None, opti=False, mode="NORMAL"):
        self.cube = Cube(debug=debug, str_position=str_position, colors=colors)
        self.debug = debug
        self.opti = opti
        self.mode = mode
        self.translation_map = [TRANSLATION_MAP[0], TRANSLATION_MAP[0]]
        self.backup_data = []

    def backup(self):
        self.backup_data.append({"cube_str":self.cube.get_str_position(), })
         
        return
    
    def restore(self):
        b = self.backup_data.pop()
        self.cube.set_str_position(b["cube_str"])
        return

    def format_with_mode(self, notations):
        notations = notations.split(" ")
        formatted = []
        counter = 0
        while counter < len(notations):
            if self.debug: print 
            formatted.append(self.translate(notations[counter], 0, -1))
            if self.debug: raw_input("formatted=%s >" % str(formatted))
            if len(formatted) >= 2 and formatted[-2][0] == formatted[-1][0]: # this routine can be used for other modes
                if formatted[-2] == formatted[-1]:
                    formatted.pop()
                    prev = formatted.pop()
                    formatted.append(prev[0]+"2")
                    if self.debug: print "doubling", prev
                else: # canceling
                    formatted.pop()
                    if self.debug: print "canceling ", formatted.pop()
                    continue
                
            if not formatted[-1] in MODES[self.mode]:
                self.cube.run(formatted[-1], quiet=True)
            else: # should rotate whole cube
                succ_flag = False
                p = formatted.pop()
                for t in ["(r)"]:
                    formatted.append(t)
                    self.backup() ##
                    self.cube.run(formatted[-1], quiet=True)
                    self.translation_map.append(TRANSLATION_MAP[ROTATED_CENTER_COLORS.index(self.cube.center_colors)])
                    formatted.append(self.translate(p, -2, -1))
                    if self.debug: print "rotating", formatted, t, p
                    if not formatted[-1] in MODES[self.mode]:
                        succ_flag = True
                        break
                    else:
                        p = formatted.pop()
                        formatted.pop()
                        self.translation_map.pop()
                        self.restore() ##
                if not succ_flag:
                    raise ValueError
                self.cube.run(formatted[-1], quiet=True)
            counter += 1

        return " ".join(formatted), len(formatted)

    def translate(self, notation, prev_index=-2, cur_index=-1):
        if self.debug:
            print "[*] translating"
            print "%d:" % prev_index, self.translation_map[prev_index]
            print "%d:" % cur_index, self.translation_map[cur_index]
            print "%s =>" % notation, 
            print "%s" % self.translation_map[cur_index][self.translation_map[prev_index].index(notation)]
        return self.translation_map[cur_index][self.translation_map[prev_index].index(notation)]

    def optimalize(self, notations):
        print "[*] Starting <optiqtm>..."
        print 
        #print "cwd =", os.path.join(os.getcwd(), os.path.dirname(__file__))
        p = Popen("echo \"%s\"| ./optiqtm" % notations, shell=True, stdout=PIPE,
                  cwd=os.path.join(os.getcwd(), os.path.dirname(__file__)))
        depth_start = False
        opt_solu = None
        for line in p.stdout.readlines():
            print line
            if depth_start:
                if line.startswith("depth"):
                    pass
                else:
                    opt_solu = line
                    break
            else:
                if line.startswith("depth"):
                    depth_start = True
                else:
                    pass
                
        if not opt_solu:
            print "Error:"
            print "<optqtm> failed. Ignoring..."
            return notations
        else:
            return opt_solu.split("  ")[0]

    def run_twophase(self):
        start_time = datetime.datetime.now()
        self.cube.show_faces()
        #print self.cube.facelets()
        r = Search.solution(self.cube.facelets(), MAX_DEPTH, TIME_OUT, False).strip() ## this is HTM
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
            print "[*] Solution found!!"
            print "first solution =", r, "(%d moves)" % len(r.split(" "))
            # optimalize
            if self.opti:
                r = self.optimalize(r) ## will be QTM
            # format with mode
            r, l = self.format_with_mode(r) ## to be HTM and follow with mode
            print "=>", r, "(%d moves)" % l
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
    parser.add_option("-o", "--optimalize", dest="opti",
                      action="store_true", default=False,
                      help="enable optimalization")
    parser.add_option("-m", "--mode", dest="mode", metavar="MODE",
                      action="store", type="string", default="NORMAL",
                      help="specify move-notations mode[NORMAL, ROBOT] (default is NORMAL)")
    parser.add_option("-e", "--out_stderr", dest="out_stderr",
                      action="store_true", default=False,
                      help="output result to stderr (for robot_commu.py)")
    (options, args) = parser.parse_args()

    if len(args) > 0:
        if options.mode in MODES:
            s = Solver(colors=args[0], debug=options.debug, opti=options.opti, mode=options.mode)
            r = s.run_twophase()
            if options.out_stderr:
                sys.stderr.write(r)
        else:
            parser.print_help()
    else: # there's no FACE_VIEW
        if options.scramble:
            s = Solver(debug=options.debug, opti=options.opti, mode=options.mode)
            s.cube.scramble()
            r = s.run_twophase()
            if options.out_stderr:
                sys.stderr.write(r)
        else:
            parser.print_help()
