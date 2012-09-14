#!/usr/bin/env python
#-*- coding:utf-8 -*-

from subprocess import Popen, PIPE
import os, os.path
import sys
import time
from serial import Serial
from cube_capture import CubeCapture
from cube_def import *

# command code
START_CAPTURE = 0x10
FINISH_CAPTURE = 0x1f
START_SOLVING = 0x20
MANEUVER = 0x70
FINISH_MANEUVER = 0x7F

class SolverRobot(object):
    def __init__(self, port=None, without_robot=False, dump_file="serial.log"):
        self.without_robot = without_robot
        self.colors_list = [] # up, front, right, back, left, down

        if self.without_robot: # for debug
            self.port = open(dump_file, "wb")
        else:
            if not port:
                port = self.enum_select_device()
                
            self.port = Serial(port, 9600, timeout=10)
            print self.port
      
    def capture_cube(self):
        print "-------- starting cube_capture.py ......"
        cc = CubeCapture(without_robot=self.without_robot, next_face=self)
        
        colors_str = cc.main()
        print "-------- finished cube_capture.py !"
        if not colors_str:
            raise Exception, "cube_capture.py failed or quit"
        
        return colors_str

    def solve(self, colors):
        print "-------- starting solver.py .........."
        p = Popen("jython solver.py -e -m ROBOT \"%s\"" % colors, shell=True, stdout=sys.stdout, stderr=PIPE, 
                  cwd=os.path.join(os.getcwd(), os.path.dirname(__file__)),
                  close_fds=True)
        retcode = p.wait()
        print "-------- finished solver.py !"
        solu =  p.stderr.read()
        if (not solu) or (retcode == 255):
            raise Exception, "solver.py failed and quit"
        else:
            return solu
        
    def send_command(self, code, arg=""):
        packet = "$LL%c%s\n" % (chr(code), arg)
        packet = packet.replace("LL", chr(len(packet)%256) + chr(len(packet)/256))
        print "--------\n" + "".join(["\\x%02x" % ord(c) for c in packet]) + "\n--------"
        self.port.write(packet)
        if self.without_robot: # for debug
            print "[*] called send_command(0x%x, %s)" % (code, arg)
            print "[*] writing to the dump file..."
            return len(packet)
        #print self.port
        #recv = self.port.readline()
        #print "".join(["\\x%02x" % ord(c) for c in recv])
        #if recv == "#\x00\x04%c\n" % chr(code+0x80):
        #    return len(packet)
        #else:
        #    raise IOError, "Robot didn't reply correct data!"
        
    def recv_command(self, code):
        if self.without_robot:
            print "[*] called recv_command(0x%x)" % (code)
            return
        #recv = self.port.read(5)
        #if recv == "#\x00\x04%c\n" % chr(code+0x80):
        #    packet = "$LL%c\n" % chr(code)
        #    packet = packet.replace("LL", chr(len(packet)%256) + chr(len(packet)/256))
        #    self.port.write(packet)
        #    return len(recv)
        #else:
        #    raise IOError, "Robot sent unexpected data!"
        
    def main(self):
        self.send_command(START_CAPTURE)
        time.sleep(1) ##
        colors = self.capture_cube()
        self.send_command(FINISH_CAPTURE)
        time.sleep(1) ##
        print "captured colors:", colors
        
        r = self.solve(colors)
        
        self.send_command(START_SOLVING)
        time.sleep(1)
        self.send_command(MANEUVER, r)
        #self.recv_command(FINISH_MANEUVER)
        
        self.port.close()
        return
    
    def enum_select_device(self):
        devlist = []
        counter = 1
        for dname in os.listdir("/dev/"):
            if dname.startswith("tty."):
                devlist.append("/dev/"+dname)
                print "%d. /dev/%s" % (counter, dname)
                counter += 1
        dnum_str = raw_input("device number >")
        try:
            dnum = int(dnum_str)
            devname = devlist[dnum-1]
        except:
            raise ValueError, "Please enter valid device number!"
        else:
            return devname


if __name__ == "__main__":
    from optparse import OptionParser

    parser = OptionParser("Usage: ./%prog [options] [DEVICE_NAME]")
    parser.add_option("-e", "--enum_device", dest="enum_device",
                      action="store_true", default=False,
                      help="enumerate and select device name (ignore DEVICE_NAME)")
    parser.add_option("-d", "--debug", dest="debug",
                      action="store_true", default=False,
                      help="enable debug mode(withoout robot)")
    parser.add_option("-o", "--dump_file", dest="dump_file", metavar="FILEPATH",
                      action="store", default="serial.log",
                      help="specify dump file of serial simulation for debug(default is \"serial.log\")")
    (options, args) = parser.parse_args()

    port = False
    if len(args) > 0:
        port = args[0]
    if options.enum_device:
        port = None
    
    if port == False: # not specified DEVICE_NAME
        if options.debug: # for debug
            robot = SolverRobot(without_robot=True, dump_file=options.dump_file)
            robot.main()
        else:
            parser.print_help()

    else: # for normal use
        robot = SolverRobot(port=port)
        robot.main()
    

