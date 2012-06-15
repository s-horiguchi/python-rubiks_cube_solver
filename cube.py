#!/usr/bin/env python
#-*- coding:utf-8 -*-

import random
from cube_def import *

class Piece(object):
    def __init__(self, num, color=None):
        self.num = num
        if not color:
            self.color = PIECES[num]

    def __repr__(self):
        ret = "<Piece(%d,[" % (self.num)
        for c in self.color:
            if c != None: ret += (COLOR[c]+"|")
            else: ret += ("N|")
        ret += "]>"
        return ret
    
    def rotate(self, face):
        # dire: 動かした面の定数
        org = self.color[:]
        if face == Right:
            self.color = [org[Right], org[Left], org[Back], org[Front], org[Up], org[Bottom]]
        elif face == Left:
            self.color = [org[Right], org[Left], org[Front], org[Back], org[Bottom], org[Up]]
        elif face == Up:
            self.color = [org[Front], org[Back], org[Up], org[Bottom], org[Left], org[Right]]
        elif face == Bottom:
            self.color = [org[Back], org[Front], org[Up], org[Bottom], org[Right], org[Left]]
        elif face == Front:
            self.color = [org[Bottom], org[Up], org[Right], org[Left], org[Front], org[Back]]
        elif face == Back:
            self.color = [org[Up], org[Bottom], org[Left], org[Right], org[Front], org[Back]]
        return self
    
    def get_color(self, face):
        # face: 欲しい面の定数
        #print self
        return COLOR[self.color[face]]
    
class Cube(object):
    def __init__(self, is_scrambled=False):
        self.pieces = [Piece(i) for i in range(26)]
        if is_scrambled:
            self.scramble()

    def scramble(self, nmoves=None):
        if not nmoves: nmoves = NUM_SCRAMBLE_MOVES
        assert type(nmoves) == int, "type error of the number of scramble moves"  #
        batch = ""
        for i in xrange(nmoves):
            batch += random.choice(ROTATE_WAYS)
        self.run(batch)
        return
        
    def R(self):
        print "<R>"
        org = self.pieces[:]
        self.pieces[L_URB] = org[L_DRB].rotate(Right)
        self.pieces[L_UR] = org[L_RB].rotate(Right)
        self.pieces[L_URF] = org[L_URB].rotate(Right)
        self.pieces[L_RF] = org[L_UR].rotate(Right)
        self.pieces[L_DRF] = org[L_URF].rotate(Right)
        self.pieces[L_DR] = org[L_RF].rotate(Right)
        self.pieces[L_DRB] = org[L_DRF].rotate(Right)
        self.pieces[L_RB] = org[L_DR].rotate(Right)
        return

    def R_(self):
        print "<R'>"
        org = self.pieces[:]
        self.pieces[L_URB] = org[L_URF].rotate(Left)
        self.pieces[L_UR] = org[L_RF].rotate(Left)
        self.pieces[L_URF] = org[L_DRF].rotate(Left)
        self.pieces[L_RF] = org[L_DR].rotate(Left)
        self.pieces[L_DRF] = org[L_DRB].rotate(Left)
        self.pieces[L_DR] = org[L_RB].rotate(Left)
        self.pieces[L_DRB] = org[L_URB].rotate(Left)
        self.pieces[L_RB] = org[L_UR].rotate(Left)
        return

    def R2(self):
        print "<R2>"
        org = self.pieces[:]
        self.pieces[L_URB] = org[L_DRF].rotate(Right).rotate(Right)
        self.pieces[L_UR] = org[L_DR].rotate(Right).rotate(Right)
        self.pieces[L_URF] = org[L_DRB].rotate(Right).rotate(Right)
        self.pieces[L_RF] = org[L_RB].rotate(Right).rotate(Right)
        self.pieces[L_DRF] = org[L_URB].rotate(Right).rotate(Right)
        self.pieces[L_DR] = org[L_UR].rotate(Right).rotate(Right)
        self.pieces[L_DRB] = org[K_URF].rotate(Right).rotate(Right)
        self.pieces[L_RB] = org[RF].rotate(Right).rotate(Right)
        return
    
    def L(self):
        print "<L>"
        org = self.pieces[:]
        self.pieces[L_ULB] = org[L_ULF].rotate(Left)
        self.pieces[L_UL] = org[L_LF].rotate(Left)
        self.pieces[L_ULF] = org[L_DLF].rotate(Left)
        self.pieces[L_LF] = org[L_DL].rotate(Left)
        self.pieces[L_DLF] = org[L_DLB].rotate(Left)
        self.pieces[L_DL] = org[L_LB].rotate(Left)
        self.pieces[L_DLB] = org[L_ULB].rotate(Left)
        self.pieces[L_LB] = org[L_UB].rotate(Left)
        return

    def L_(self):
        print "<L'>"
        org = self.pieces[:]
        self.pieces[L_ULB] = org[L_DLB].rotate(Right)
        self.pieces[L_UL] = org[L_LB].rotate(Right)
        self.pieces[L_ULF] = org[L_ULB].rotate(Right)
        self.pieces[L_LF] = org[L_UB].rotate(Right)
        self.pieces[L_DLF] = org[L_ULF].rotate(Right)
        self.pieces[L_DL] = org[L_LF].rotate(Right)
        self.pieces[L_DLB] = org[L_DLF].rotate(Right)
        self.pieces[L_LB] = org[L_DL].rotate(Right)
        return

    def L2(self):
        print "<L2>"
        org = self.pieces[:]
        self.pieces[L_ULB] = org[L_DLF].rotate(Left).rotate(Left)
        self.pieces[L_UL] = org[L_DL].rotate(Left).rotate(Left)
        self.pieces[L_ULF] = org[L_DLB].rotate(Left).rotate(Left)
        self.pieces[L_LF] = org[L_LB].rotate(Left).rotate(Left)
        self.pieces[L_DLF] = org[L_ULB].rotate(Left).rotate(Left)
        self.pieces[L_DL] = org[L_UL].rotate(Left).rotate(Left)
        self.pieces[L_DLB] = org[L_ULF].rotate(Left).rotate(Left)
        self.pieces[L_LB] = org[L_LF].rotate(Left).rotate(Left)
        return
    
    def U(self):
        print "<U>"
        org = self.pieces[:]
        self.pieces[L_URB] = org[L_URF].rotate(Up)
        self.pieces[L_UR] = org[L_UF].rotate(Up)
        self.pieces[L_URF] = org[L_ULF].rotate(Up)
        self.pieces[L_UF] = org[L_UL].rotate(Up)
        self.pieces[L_ULF] = org[L_ULB].rotate(Up)
        self.pieces[L_UL] = org[L_UB].rotate(Up)
        self.pieces[L_ULB] = org[L_URB].rotate(Up)
        self.pieces[L_UB] = org[L_UR].rotate(Up)
        return
    
    def U_(self):
        print "<U'>"
        org = self.pieces[:]
        self.pieces[L_URB] = org[L_ULB].rotate(Bottom)
        self.pieces[L_UR] = org[L_UB].rotate(Bottom)
        self.pieces[L_URF] = org[L_URB].rotate(Bottom)
        self.pieces[L_UF] = org[L_UR].rotate(Bottom)
        self.pieces[L_ULF] = org[L_URF].rotate(Bottom)
        self.pieces[L_UL] = org[L_UF].rotate(Bottom)
        self.pieces[L_ULB] = org[L_ULF].rotate(Bottom)
        self.pieces[L_UB] = org[L_UL].rotate(Bottom)
        return

    def U2(self):
        print "<U2>"
        org = self.pieces[:]
        self.pieces[L_URB] = org[L_ULF].rotate(Up).rotate(Up)
        self.pieces[L_UR] = org[L_UL].rotate(Up).rotate(Up)
        self.pieces[L_URF] = org[L_ULB].rotate(Up).rotate(Up)
        self.pieces[L_UF] = org[L_UB].rotate(Up).rotate(Up)
        self.pieces[L_ULF] = org[L_URB].rotate(Up).rotate(Up)
        self.pieces[L_UL] = org[L_UR].rotate(Up).rotate(Up)
        self.pieces[L_ULB] = org[L_URF].rotate(Up).rotate(Up)
        self.pieces[L_UB] = org[L_UF].rotate(Up).rotate(Up)
        return
    
    def D(self):
        print "<D>"
        org = self.pieces[:]
        self.pieces[L_DRB] = org[L_DLB].rotate(Bottom)
        self.pieces[L_DR] = org[L_DB].rotate(Bottom)
        self.pieces[L_DRF] = org[L_DRB].rotate(Bottom)
        self.pieces[L_DF] = org[L_DR].rotate(Bottom)
        self.pieces[L_DLF] = org[L_DRF].rotate(Bottom)
        self.pieces[L_DL] = org[L_DF].rotate(Bottom)
        self.pieces[L_DLB] = org[L_DLF].rotate(Bottom)
        self.pieces[L_DB] = org[L_DL].rotate(Bottom)
        return

    def D_(self):
        print "<D'>"
        org = self.pieces[:]
        self.pieces[L_DRB] = org[L_DRF].rotate(Up)
        self.pieces[L_DR] = org[L_DF].rotate(Up)
        self.pieces[L_DRF] = org[L_DLF].rotate(Up)
        self.pieces[L_DF] = org[L_DL].rotate(Up)
        self.pieces[L_DLF] = org[L_DLB].rotate(Up)
        self.pieces[L_DL] = org[L_DB].rotate(Up)
        self.pieces[L_DLB] = org[L_DRB].rotate(Up)
        self.pieces[L_DB] = org[L_DR].rotate(Up)
        return

    def D2(self):
        print "<D2>"
        org = self.pieces[:]
        self.pieces[L_DRB] = org[L_DLF].rotate(Bottom).rotate(Bottom)
        self.pieces[L_DR] = org[L_DL].rotate(Bottom).rotate(Bottom)
        self.pieces[L_DRF] = org[L_DLB].rotate(Bottom).rotate(Bottom)
        self.pieces[L_DF] = org[L_DB].rotate(Bottom).rotate(Bottom)
        self.pieces[L_DLF] = org[L_DRB].rotate(Bottom).rotate(Bottom)
        self.pieces[L_DL] = org[L_DR].rotate(Bottom).rotate(Bottom)
        self.pieces[L_DLB] = org[L_DRF].rotate(Bottom).rotate(Bottom)
        self.pieces[L_DB] = org[L_DF].rotate(Bottom).rotate(Bottom)
        return

    def F(self):
        print "<F>"
        org = self.pieces[:]
        self.pieces[L_URF] = org[L_DRF].rotate(Front)
        self.pieces[L_RF] = org[L_DF].rotate(Front)
        self.pieces[L_DRF] = org[L_DLF].rotate(Front)
        self.pieces[L_DF] = org[L_LF].rotate(Front)
        self.pieces[L_DLF] = org[L_ULF].rotate(Front)
        self.pieces[L_LF] = org[L_UF].rotate(Front)
        self.pieces[L_ULF] = org[L_URF].rotate(Front)
        self.pieces[L_UF] = org[L_RF].rotate(Front)
        return

    def F_(self):
        print "<F'>"
        org = self.pieces[:]
        self.pieces[L_URF] = org[L_ULF].rotate(Back)
        self.pieces[L_RF] = org[L_UF].rotate(Back)
        self.pieces[L_DRF] = org[L_URF].rotate(Back)
        self.pieces[L_DF] = org[L_RF].rotate(Back)
        self.pieces[L_DLF] = org[L_DRF].rotate(Back)
        self.pieces[L_LF] = org[L_DF].rotate(Back)
        self.pieces[L_ULF] = org[L_DLF].rotate(Back)
        self.pieces[L_UF] = org[L_LF].rotate(Back)
        return

    def F2(self):
        print "<F2>"
        org = self.pieces[:]
        self.pieces[L_URF] = org[L_DLF].rotate(Front).rotate(Front)
        self.pieces[L_RF] = org[L_LF].rotate(Front).rotate(Front)
        self.pieces[L_DRF] = org[L_ULF].rotate(Front).rotate(Front)
        self.pieces[L_DF] = org[L_UF].rotate(Front).rotate(Front)
        self.pieces[L_DLF] = org[L_URF].rotate(Front).rotate(Front)
        self.pieces[L_LF] = org[L_RF].rotate(Front).rotate(Front)
        self.pieces[L_ULF] = org[L_DRF].rotate(Front).rotate(Front)
        self.pieces[L_UF] = org[L_DF].rotate(Front).rotate(Front)
        return
        
    def B(self):
        print "<B>"
        org = self.pieces[:]
        self.pieces[L_URB] = org[L_ULB].rotate(Back)
        self.pieces[L_RB] = org[L_UB].rotate(Back)
        self.pieces[L_DRB] = org[L_URB].rotate(Back)
        self.pieces[L_DB] = org[L_RB].rotate(Back)
        self.pieces[L_DLB] = org[L_DRB].rotate(Back)
        self.pieces[L_LB] = org[L_DB].rotate(Back)
        self.pieces[L_ULB] = org[L_DLB].rotate(Back)
        self.pieces[L_UB] = org[L_LB].rotate(Back)
        return

    def B_(self):
        print "<B'>"
        org = self.pieces[:]
        self.pieces[L_URB] = org[L_DRB].rotate(Front)
        self.pieces[L_RB] = org[L_DB].rotate(Front)
        self.pieces[L_DRB] = org[L_DLB].rotate(Front)
        self.pieces[L_DB] = org[L_LB].rotate(Front)
        self.pieces[L_DLB] = org[L_ULB].rotate(Front)
        self.pieces[L_LB] = org[L_UB].rotate(Front)
        self.pieces[L_ULB] = org[L_URB].rotate(Front)
        self.pieces[L_UB] = org[L_RB].rotate(Front)
        return

    def B2(self):
        print "<B2>"
        org = self.pieces[:]
        self.pieces[L_URB] = org[L_DLB].rotate(Back).rotate(Back)
        self.pieces[L_RB] = org[L_LB].rotate(Back).rotate(Back)
        self.pieces[L_DRB] = org[L_ULB].rotate(Back).rotate(Back)
        self.pieces[L_DB] = org[L_UB].rotate(Back).rotate(Back)
        self.pieces[L_DLB] = org[L_URB].rotate(Back).rotate(Back)
        self.pieces[L_LB] = org[L_RB].rotate(Back).rotate(Back)
        self.pieces[L_ULB] = org[L_DRB].rotate(Back).rotate(Back)
        self.pieces[L_UB] = org[L_DB].rotate(Back).rotate(Back)
        return
    
    def get_colors_on_face(self, face):
        if face == Right:
            return (self.pieces[L_URF].get_color(face),
                    self.pieces[L_UR].get_color(face),
                    self.pieces[L_URB].get_color(face),
                    self.pieces[L_RF].get_color(face),
                    self.pieces[L_R].get_color(face),
                    self.pieces[L_RB].get_color(face),
                    self.pieces[L_DRF].get_color(face),
                    self.pieces[L_DR].get_color(face),
                    self.pieces[L_DRB].get_color(face) )
        elif face == Left:
            return (self.pieces[L_ULB].get_color(face),
                    self.pieces[L_UL].get_color(face),
                    self.pieces[L_ULF].get_color(face),
                    self.pieces[L_LB].get_color(face),
                    self.pieces[L_L].get_color(face),
                    self.pieces[L_LF].get_color(face),
                    self.pieces[L_DLB].get_color(face),
                    self.pieces[L_DL].get_color(face),
                    self.pieces[L_DLF].get_color(face) )
        elif face == Up:
            return (self.pieces[L_ULB].get_color(face),
                    self.pieces[L_UB].get_color(face),
                    self.pieces[L_URB].get_color(face),
                    self.pieces[L_UL].get_color(face),
                    self.pieces[L_U].get_color(face),
                    self.pieces[L_UR].get_color(face),
                    self.pieces[L_ULF].get_color(face),
                    self.pieces[L_UF].get_color(face),
                    self.pieces[L_URF].get_color(face) )
        elif face == Bottom:
            return (self.pieces[L_DLF].get_color(face),
                    self.pieces[L_DF].get_color(face),
                    self.pieces[L_DRF].get_color(face),
                    self.pieces[L_DL].get_color(face),
                    self.pieces[L_D].get_color(face),
                    self.pieces[L_DR].get_color(face),
                    self.pieces[L_DLB].get_color(face),
                    self.pieces[L_DB].get_color(face),
                    self.pieces[L_DRB].get_color(face) )
        elif face == Front:
            return (self.pieces[L_ULF].get_color(face),
                    self.pieces[L_UF].get_color(face),
                    self.pieces[L_URF].get_color(face),
                    self.pieces[L_LF].get_color(face),
                    self.pieces[L_F].get_color(face),
                    self.pieces[L_RF].get_color(face),
                    self.pieces[L_DLF].get_color(face),
                    self.pieces[L_DF].get_color(face),
                    self.pieces[L_DRF].get_color(face) )
        elif face == Back:
            return (self.pieces[L_URB].get_color(face),
                    self.pieces[L_UB].get_color(face),
                    self.pieces[L_ULB].get_color(face),
                    self.pieces[L_RB].get_color(face),
                    self.pieces[L_B].get_color(face),
                    self.pieces[L_LB].get_color(face),
                    self.pieces[L_DRB].get_color(face),
                    self.pieces[L_DB].get_color(face),
                    self.pieces[L_DLB].get_color(face) )
        return
    
    def show_faces(self):
        print "<-- show faces -->"
        for i in range(6):
            print "%s:" % FACE[i]
            colors = self.get_colors_on_face(i)
            print colors[0:3]
            print colors[3:6]
            print colors[6:9]
        return

    def run(self, batch):
        # batch: 回転記号の文字列
        que = []
        for b in batch:
            #print b
            #print que
            if b in ["R", "L", "U", "D", "F", "B"]:
                que.append(getattr(self, b))
            elif b == "'":
                if que[-1].__name__ in ["R", "L", "U", "D", "F", "B"]:
                    que[-1] = getattr(self, que[-1].__name__+"_")
                else:
                    print "[*] 回転記号 構文エラー"
                    raise SyntaxError, "The sign before \"'\" must be 'R','L','U','D','F',or 'B'."
            elif b == "2":
                if que[-1].__name__ in ["R", "L", "U", "D", "F", "B"]:
                    que[-1] = getattr(self, que[-1].__name__+"2")
                else:
                    print "[*] "
                    raise SntaxError, "The sign before \"2\" must be 'R','L','U','D','F',or 'B'."
        for q in que:
            q()
            self.show_faces()
            raw_input() #
        return
                
    
if __name__ == "__main__":
    import sys
    c = Cube()
    c.show_faces()
    c.run(sys.argv[1])
    c.show_faces()
