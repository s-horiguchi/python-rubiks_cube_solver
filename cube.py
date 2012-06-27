#!/usr/bin/env python
#-*- coding:utf-8 -*-

import random
from cube_def import *

class Piece(object):
    def __init__(self, num, color=None):
        self.num = num
        if not color:
            self.color = PIECES[num]
        else:
            self.color = color

    def __repr__(self):
        ret = "<Piece(%d,[" % (self.num)
        for c in self.color:
            if c != None: ret += (COLOR[c]+"|")
            else: ret += ("_|")
        ret += "]>"
        return ret
    
    def rotate(self, face):
        # dire: 動かした面の定数
        org = self.color[:]
        if face == Right:
            self.color = [org[Right], org[Left], org[Front], org[Back], org[Down], org[Up]]
        elif face == Left:
            self.color = [org[Right], org[Left], org[Back], org[Front], org[Up], org[Down]]
        elif face == Up:
            self.color = [org[Back], org[Front], org[Up], org[Down], org[Right], org[Left]]
        elif face == Down:
            self.color = [org[Front], org[Back], org[Up], org[Down], org[Left], org[Right]]
        elif face == Front:
            self.color = [org[Up], org[Down], org[Left], org[Right], org[Front], org[Back]]
        elif face == Back:
            self.color = [org[Down], org[Up], org[Right], org[Left], org[Front], org[Back]]
        return self
    
    def get_color(self, face):
        # face: 欲しい面の定数
        #print self
        assert self.color[face] != NONE, "specified face is NONE"
        return self.color[face]

    def export(self, center_colors):
        color = [center_colors.index(c) for c in self.color if c != NONE]
        try:
            yield PIECES_without_NONE.index(sorted(color))
        except ValueError:
            raise
        for c in self.color:
            if c == NONE:
                yield NONE
            else:
                yield center_colors.index(c)
        
class Cube(object):
    def __init__(self, is_scrambled=False, debug=True, str_position=None, colors=None):
        # don't set <is_scramble> and <colors> (preferred colors)
        # don't set <str_position> and <colors> (preferred str_position)
        if not str_position:
            if colors:
                try:
                    colors_list = [[COLOR.index(c) for c in f] for f in colors.split("|")]
                except ValueError:
                    print "[*] invalid colors data."
                    raise
                self.set_by_faces_color(colors_list)
            else:
                self.pieces = [Piece(i) for i in range(26)]
                if is_scrambled:
                    self.scramble()
        else:
            self.pieces = [Piece(int(p.split(",")[0]), [int(c) for c in p.split(",")[1:]]) for p in str_position.split("|")]
        self.debug = debug
        self.center_colors = tuple([COLOR.index(f[4]) for f in self.show_faces(get_only=True)])
        self.translation_map = TRANSLATION_MAP[self.center_colors]

#    def get_standard_color_output(self):
#        return [[self.center_colors.index(c) for c in f] for f in self.show_faces(get_only=True)]

    def scramble(self, nmoves=None):
        if not nmoves: nmoves = NUM_SCRAMBLE_MOVES
        assert type(nmoves) == int, "type error of the number of scramble moves"  #
        batch = ""
        for i in xrange(nmoves):
            batch += random.choice(ROTATE_WAYS)
        if self.debug: print "[*] batch =", batch
        self.run(batch, False)
        return

    def set_by_faces_color(self, colors, quiet=False):
        # colors = [ <faces list> [ <colors list> RED, ...], ...]
        self.pieces = []
        for i in xrange(26):
            #print [(COLOR[colors[f[0]][f[1]]], f) for f in LOCATION[i]]
            look = [colors[f[0]][f[1]] for f in LOCATION[i]]
            try:
                pnum = PIECES_without_NONE.index(sorted(look))
            except ValueError:
                if not quiet:
                    print "[*] specified faces color is invalid!"
                    raise
                else:
                    return False
            piece = [NONE]*6
            for c,f in enumerate(LOCATION[i]):
                piece[f[0]] = look[c]
            self.pieces.append(Piece(num=pnum, color=piece))
        return True
        
    def get_str_position(self, standard=False):
        if standard:
            center_colors = self.center_colors
        else:
            center_colors = (RED, ORANGE, WHITE, BLUE, GREEN, YELLOW)
        return "|".join([",".join([str(c) for c in p.export(center_colors)]) for p in self.pieces])

    def translate_batch(self, batch): # 回転した奴向け
        new_batch = ""
        for b in batch:
            new_batch += self.translation_map[b]
        return new_batch

    def R(self, quiet=False):
        if not quiet: print "<R>"
        org = self.pieces[:]
        self.pieces[L_URB] = org[L_URF].rotate(Right)
        self.pieces[L_UR] = org[L_RF].rotate(Right)
        self.pieces[L_URF] = org[L_DRF].rotate(Right)
        self.pieces[L_RF] = org[L_DR].rotate(Right)
        self.pieces[L_DRF] = org[L_DRB].rotate(Right)
        self.pieces[L_DR] = org[L_RB].rotate(Right)
        self.pieces[L_DRB] = org[L_URB].rotate(Right)
        self.pieces[L_RB] = org[L_UR].rotate(Right)
        return

    def R_(self, quiet=False):
        if not quiet: print "<R'>"
        org = self.pieces[:]
        self.pieces[L_URB] = org[L_DRB].rotate(Left)
        self.pieces[L_UR] = org[L_RB].rotate(Left)
        self.pieces[L_URF] = org[L_URB].rotate(Left)
        self.pieces[L_RF] = org[L_UR].rotate(Left)
        self.pieces[L_DRF] = org[L_URF].rotate(Left)
        self.pieces[L_DR] = org[L_RF].rotate(Left)
        self.pieces[L_DRB] = org[L_DRF].rotate(Left)
        self.pieces[L_RB] = org[L_DR].rotate(Left)
        return

    def R2(self, quiet=False):
        if not quiet: print "<R2>"
        org = self.pieces[:]
        self.pieces[L_URB] = org[L_DRF].rotate(Right).rotate(Right)
        self.pieces[L_UR] = org[L_DR].rotate(Right).rotate(Right)
        self.pieces[L_URF] = org[L_DRB].rotate(Right).rotate(Right)
        self.pieces[L_RF] = org[L_RB].rotate(Right).rotate(Right)
        self.pieces[L_DRF] = org[L_URB].rotate(Right).rotate(Right)
        self.pieces[L_DR] = org[L_UR].rotate(Right).rotate(Right)
        self.pieces[L_DRB] = org[L_URF].rotate(Right).rotate(Right)
        self.pieces[L_RB] = org[L_RF].rotate(Right).rotate(Right)
        return
    
    def r(self, quiet=False):
        if not quiet: print "<(r)>"
        self.R(quiet=True)
        self.L_(quiet=True)
        self.M_(quiet=True)
        return

    def r_(self, quiet=False):
        if not quiet: print "<(r')>"
        self.R_(quiet=True)
        self.L(quiet=True)
        self.M(quiet=True)
        return
    
    def L(self, quiet=False):
        if not quiet: print "<L>"
        org = self.pieces[:]
        self.pieces[L_ULB] = org[L_DLB].rotate(Left)
        self.pieces[L_UL] = org[L_LB].rotate(Left)
        self.pieces[L_ULF] = org[L_ULB].rotate(Left)
        self.pieces[L_LF] = org[L_UL].rotate(Left)
        self.pieces[L_DLF] = org[L_ULF].rotate(Left)
        self.pieces[L_DL] = org[L_LF].rotate(Left)
        self.pieces[L_DLB] = org[L_DLF].rotate(Left)
        self.pieces[L_LB] = org[L_DL].rotate(Left)
        return

    def L_(self, quiet=False):
        if not quiet: print "<L'>"
        org = self.pieces[:]
        self.pieces[L_ULB] = org[L_ULF].rotate(Right)
        self.pieces[L_UL] = org[L_LF].rotate(Right)
        self.pieces[L_ULF] = org[L_DLF].rotate(Right)
        self.pieces[L_LF] = org[L_DL].rotate(Right)
        self.pieces[L_DLF] = org[L_DLB].rotate(Right)
        self.pieces[L_DL] = org[L_LB].rotate(Right)
        self.pieces[L_DLB] = org[L_ULB].rotate(Right)
        self.pieces[L_LB] = org[L_UL].rotate(Right)
        return

    def L2(self, quiet=False):
        if not quiet: print "<L2>"
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
    
    def U(self, quiet=False):
        if not quiet: print "<U>"
        org = self.pieces[:]
        self.pieces[L_URB] = org[L_ULB].rotate(Up)
        self.pieces[L_UR] = org[L_UB].rotate(Up)
        self.pieces[L_URF] = org[L_URB].rotate(Up)
        self.pieces[L_UF] = org[L_UR].rotate(Up)
        self.pieces[L_ULF] = org[L_URF].rotate(Up)
        self.pieces[L_UL] = org[L_UF].rotate(Up)
        self.pieces[L_ULB] = org[L_ULF].rotate(Up)
        self.pieces[L_UB] = org[L_UL].rotate(Up)
        return
    
    def U_(self, quiet=False):
        if not quiet: print "<U'>"
        org = self.pieces[:]
        self.pieces[L_URB] = org[L_URF].rotate(Down)
        self.pieces[L_UR] = org[L_UF].rotate(Down)
        self.pieces[L_URF] = org[L_ULF].rotate(Down)
        self.pieces[L_UF] = org[L_UL].rotate(Down)
        self.pieces[L_ULF] = org[L_ULB].rotate(Down)
        self.pieces[L_UL] = org[L_UB].rotate(Down)
        self.pieces[L_ULB] = org[L_URB].rotate(Down)
        self.pieces[L_UB] = org[L_UR].rotate(Down)
        return

    def U2(self, quiet=False):
        if not quiet: print "<U2>"
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
    
    def u(self, quiet=False):
        if not quiet: print "<(u)>"
        self.U(quiet=True)
        self.E_(quiet=True)
        self.D_(quiet=True)
        return

    def u_(self, quiet=False):
        if not quiet: print "<(u')>"
        self.U_(quiet=True)
        self.E(quiet=True)
        self.D(quiet=True)
        return
        
    def D(self, quiet=False):
        if not quiet: print "<D>"
        org = self.pieces[:]
        self.pieces[L_DRB] = org[L_DRF].rotate(Down)
        self.pieces[L_DR] = org[L_DF].rotate(Down)
        self.pieces[L_DRF] = org[L_DLF].rotate(Down)
        self.pieces[L_DF] = org[L_DL].rotate(Down)
        self.pieces[L_DLF] = org[L_DLB].rotate(Down)
        self.pieces[L_DL] = org[L_DB].rotate(Down)
        self.pieces[L_DLB] = org[L_DRB].rotate(Down)
        self.pieces[L_DB] = org[L_DR].rotate(Down)
        return

    def D_(self, quiet=False):
        if not quiet: print "<D'>"
        org = self.pieces[:]
        self.pieces[L_DRB] = org[L_DLB].rotate(Up)
        self.pieces[L_DR] = org[L_DB].rotate(Up)
        self.pieces[L_DRF] = org[L_DRB].rotate(Up)
        self.pieces[L_DF] = org[L_DR].rotate(Up)
        self.pieces[L_DLF] = org[L_DRF].rotate(Up)
        self.pieces[L_DL] = org[L_DF].rotate(Up)
        self.pieces[L_DLB] = org[L_DLF].rotate(Up)
        self.pieces[L_DB] = org[L_DL].rotate(Up)
        return

    def D2(self, quiet=False):
        if not quiet: print "<D2>"
        org = self.pieces[:]
        self.pieces[L_DRB] = org[L_DLF].rotate(Down).rotate(Down)
        self.pieces[L_DR] = org[L_DL].rotate(Down).rotate(Down)
        self.pieces[L_DRF] = org[L_DLB].rotate(Down).rotate(Down)
        self.pieces[L_DF] = org[L_DB].rotate(Down).rotate(Down)
        self.pieces[L_DLF] = org[L_DRB].rotate(Down).rotate(Down)
        self.pieces[L_DL] = org[L_DR].rotate(Down).rotate(Down)
        self.pieces[L_DLB] = org[L_DRF].rotate(Down).rotate(Down)
        self.pieces[L_DB] = org[L_DF].rotate(Down).rotate(Down)
        return

    def F(self, quiet=False):
        if not quiet: print "<F>"
        org = self.pieces[:]
        self.pieces[L_URF] = org[L_ULF].rotate(Front)
        self.pieces[L_RF] = org[L_UF].rotate(Front)
        self.pieces[L_DRF] = org[L_URF].rotate(Front)
        self.pieces[L_DF] = org[L_RF].rotate(Front)
        self.pieces[L_DLF] = org[L_DRF].rotate(Front)
        self.pieces[L_LF] = org[L_DF].rotate(Front)
        self.pieces[L_ULF] = org[L_DLF].rotate(Front)
        self.pieces[L_UF] = org[L_LF].rotate(Front)
        return

    def F_(self, quiet=False):
        if not quiet: print "<F'>"
        org = self.pieces[:]
        self.pieces[L_URF] = org[L_DRF].rotate(Back)
        self.pieces[L_RF] = org[L_DF].rotate(Back)
        self.pieces[L_DRF] = org[L_DLF].rotate(Back)
        self.pieces[L_DF] = org[L_LF].rotate(Back)
        self.pieces[L_DLF] = org[L_ULF].rotate(Back)
        self.pieces[L_LF] = org[L_UF].rotate(Back)
        self.pieces[L_ULF] = org[L_URF].rotate(Back)
        self.pieces[L_UF] = org[L_RF].rotate(Back)
        return

    def F2(self, quiet=False):
        if not quiet: print "<F2>"
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
        
    def f(self, quiet=False):
        if not quiet: print "<(f)>"
        self.F(quiet=True)
        self.S(quiet=True)
        self.B_(quiet=True)
        return

    def f_(self, quiet=False):
        if not quiet: print "<(f')>"
        self.F_(quiet=True)
        self.S_(quiet=True)
        self.B(quiet=True)
        return

    def B(self, quiet=False):
        if not quiet: print "<B>"
        org = self.pieces[:]
        self.pieces[L_URB] = org[L_DRB].rotate(Back)
        self.pieces[L_RB] = org[L_DB].rotate(Back)
        self.pieces[L_DRB] = org[L_DLB].rotate(Back)
        self.pieces[L_DB] = org[L_LB].rotate(Back)
        self.pieces[L_DLB] = org[L_ULB].rotate(Back)
        self.pieces[L_LB] = org[L_UB].rotate(Back)
        self.pieces[L_ULB] = org[L_URB].rotate(Back)
        self.pieces[L_UB] = org[L_RB].rotate(Back)
        return

    def B_(self, quiet=False):
        if not quiet: print "<B'>"
        org = self.pieces[:]
        self.pieces[L_URB] = org[L_ULB].rotate(Front)
        self.pieces[L_RB] = org[L_UB].rotate(Front)
        self.pieces[L_DRB] = org[L_URB].rotate(Front)
        self.pieces[L_DB] = org[L_RB].rotate(Front)
        self.pieces[L_DLB] = org[L_DRB].rotate(Front)
        self.pieces[L_LB] = org[L_DB].rotate(Front)
        self.pieces[L_ULB] = org[L_DLB].rotate(Front)
        self.pieces[L_UB] = org[L_LB].rotate(Front)
        return

    def B2(self, quiet=False):
        if not quiet: print "<B2>"
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
    
    def M(self, quiet=False):
        if not quiet: print "<M>"
        org = self.pieces[:]
        self.pieces[L_UB] = org[L_DB].rotate(Left)
        self.pieces[L_U] = org[L_B].rotate(Left)
        self.pieces[L_UF] = org[L_UB].rotate(Left)
        self.pieces[L_F] = org[L_U].rotate(Left)
        self.pieces[L_DF] = org[L_UF].rotate(Left)
        self.pieces[L_D] = org[L_F].rotate(Left)
        self.pieces[L_DB] = org[L_DF].rotate(Left)
        self.pieces[L_B] = org[L_D].rotate(Left)
        return

    def M_(self, quiet=False):
        if not quiet: print "<M'>"
        org = self.pieces[:]
        self.pieces[L_UB] = org[L_UF].rotate(Right)
        self.pieces[L_U] = org[L_F].rotate(Right)
        self.pieces[L_UF] = org[L_DF].rotate(Right)
        self.pieces[L_F] = org[L_D].rotate(Right)
        self.pieces[L_DF] = org[L_DB].rotate(Right)
        self.pieces[L_D] = org[L_B].rotate(Right)
        self.pieces[L_DB] = org[L_UB].rotate(Right)
        self.pieces[L_B] = org[L_U].rotate(Right)
        return

    def M2(self, quiet=False):
        if not quiet: print "<M2>"
        org = self.pieces[:]
        self.pieces[L_UB] = org[L_DF].rotate(Left).rotate(Left)
        self.pieces[L_U] = org[L_D].rotate(Left).rotate(Left)
        self.pieces[L_UF] = org[L_DB].rotate(Left).rotate(Left)
        self.pieces[L_F] = org[L_B].rotate(Left).rotate(Left)
        self.pieces[L_DF] = org[L_UB].rotate(Left).rotate(Left)
        self.pieces[L_D] = org[L_U].rotate(Left).rotate(Left)
        self.pieces[L_DB] = org[L_UF].rotate(Left).rotate(Left)
        self.pieces[L_B] = org[L_F].rotate(Left).rotate(Left)
        return
        
    def E(self, quiet=False):
        if not quiet:print "<E>"
        org = self.pieces[:]
        self.pieces[L_LF] = org[L_LB].rotate(Down)
        self.pieces[L_F] = org[L_L].rotate(Down)
        self.pieces[L_RF] = org[L_LF].rotate(Down)
        self.pieces[L_R] = org[L_F].rotate(Down)
        self.pieces[L_RB] = org[L_RF].rotate(Down)
        self.pieces[L_B] = org[L_R].rotate(Down)
        self.pieces[L_LB] = org[L_RB].rotate(Down)
        self.pieces[L_L] = org[L_B].rotate(Down)
        return

    def E_(self, quiet=False):
        if not quiet:print "<E'>"
        org = self.pieces[:]
        self.pieces[L_LF] = org[L_RF].rotate(Up)
        self.pieces[L_F] = org[L_R].rotate(Up)
        self.pieces[L_RF] = org[L_RB].rotate(Up)
        self.pieces[L_R] = org[L_B].rotate(Up)
        self.pieces[L_RB] = org[L_LB].rotate(Up)
        self.pieces[L_B] = org[L_K].rotate(Up)
        self.pieces[L_LB] = org[L_LF].rotate(Up)
        self.pieces[L_L] = org[L_F].rotate(Up)
        return

    def E2(self, quiet=False):
        if not quiet:print "<E2>"
        org = self.pieces[:]
        self.pieces[L_LF] = org[L_RB].rotate(Down).rotate(Down)
        self.pieces[L_F] = org[L_B].rotate(Down).rotate(Down)
        self.pieces[L_RF] = org[L_LB].rotate(Down).rotate(Down)
        self.pieces[L_R] = org[L_L].rotate(Down).rotate(Down)
        self.pieces[L_RB] = org[L_LF].rotate(Down).rotate(Down)
        self.pieces[L_B] = org[L_F].rotate(Down).rotate(Down)
        self.pieces[L_LB] = org[L_RF].rotate(Down).rotate(Down)
        self.pieces[L_L] = org[L_R].rotate(Down).rotate(Down)
        return

    def S(self, quiet=False):
        if not quiet: print "<S>"
        org = self.pieces[:]
        self.pieces[L_UR] = org[L_UL].rotate(Front)
        self.pieces[L_R] = org[L_U].rotate(Front)
        self.pieces[L_DR] = org[L_UR].rotate(Front)
        self.pieces[L_D] = org[L_R].rotate(Front)
        self.pieces[L_DL] = org[L_DR].rotate(Front)
        self.pieces[L_L] = org[L_D].rotate(Front)
        self.pieces[L_UL] = org[L_DL].rotate(Front)
        self.pieces[L_U] = org[L_L].rotate(Front)
        return

    def S_(self, quiet=False):
        if not quiet: print "<S'>"
        org = self.pieces[:]
        self.pieces[L_UR] = org[L_DR].rotate(Back)
        self.pieces[L_R] = org[L_D].rotate(Back)
        self.pieces[L_DR] = org[L_DL].rotate(Back)
        self.pieces[L_D] = org[L_L].rotate(Back)
        self.pieces[L_DL] = org[L_UL].rotate(Back)
        self.pieces[L_L] = org[L_U].rotate(Back)
        self.pieces[L_UL] = org[L_UR].rotate(Back)
        self.pieces[L_U] = org[L_R].rotate(Back)
        return

    def S2(self, quiet=False):
        if not quiet: print "<S2>"
        org = self.pieces[:]
        self.pieces[L_UR] = org[L_DL].rotate(Front).rotate(Front)
        self.pieces[L_R] = org[L_L].rotate(Front).rotate(Front)
        self.pieces[L_DR] = org[L_UL].rotate(Front).rotate(Front)
        self.pieces[L_D] = org[L_U].rotate(Front).rotate(Front)
        self.pieces[L_DL] = org[L_UR].rotate(Front).rotate(Front)
        self.pieces[L_L] = org[L_R].rotate(Front).rotate(Front)
        self.pieces[L_UL] = org[L_DR].rotate(Front).rotate(Front)
        self.pieces[L_U] = org[L_D].rotate(Front).rotate(Front)
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
        elif face == Down:
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
    
    def show_faces(self, get_only=False, standard=False, color_num=False):
        if not get_only: print "<-- show faces -->"
        if self.debug and not get_only:
            print "str_position:"
            print self.get_str_position(standard)
        ret = []
        #
        if standard:
            center_colors = self.center_colors
        else:
            center_colors = (RED, ORANGE, WHITE, BLUE, GREEN, YELLOW)
            
        for i in range(6):
            colors = [center_colors.index(c) for c in self.get_colors_on_face(i)]
            if not color_num:
                colors = [COLOR[c] for c in colors]
            if not get_only:
                print "%s:" % FACE[i]
                print colors[0:3]
                print colors[3:6]
                print colors[6:9]
            ret.append(colors)
        return ret

    def run(self, batch, confirm=False, quiet=False):
        # batch: 回転記号の文字列
        if not quiet: print "[*]", batch
        que = []
        in_entire_checking = False
        for b in batch:
            #print b
            #print que
            if in_entire_checking:
                if b == ")":
                    in_entire_checking = False
                    continue
                elif ("(%c)" % b) in ENTIRE_ROTATE_WAYS:
                    que.append(getattr(self, b))
                    continue
                else:
                    print "[*] 回転記号 構文エラー"
                    if not quiet:
                        raise SyntaxError, "The sign surrounded by \"( )\" must be in " + str(ENTIRE_ROTATE_WAYS)
                    else:
                        return
            if b in SINGLE_ROTATE_WAYS:
                que.append(getattr(self, b))
            elif b == "'":
                if que[-1].__name__ in SINGLE_ROTATE_WAYS:
                    que[-1] = getattr(self, que[-1].__name__+"_")
                else:
                    print "[*] 回転記号 構文エラー"
                    if not quiet:
                        raise SyntaxError, "The sign before \"'\" must be in " + str(SINGLE_ROTATE_WAYS)
                    else:
                        return
            elif b == "2":
                if que[-1].__name__ in SINGLE_ROTATE_WAYS:
                    que[-1] = getattr(self, que[-1].__name__+"2")
                else:
                    print "[*] 回転記号 構文エラー"
                    if not quiet:
                        raise SyntaxError, "The sign before \"2\" must be in " + str(SNGLE_ROTATE_WAYS)
                    else:
                        return
            elif b == "(":
                in_entire_checking = True
            else:
                print "[*] 回転記号 構文エラー"
                return
        for q in que:
            q()
            if self.debug: self.show_faces()
            if confirm:
                raw_input() 
        return len(que)
    
    def game(self):
        print "<-- GAME MODE -->"
        print "Let's move in many ways!"
        print
        while 1:
            print "Enter some move notations or 'quit' to quit this program."
            ri = raw_input(">")
            if ri.strip() == "quit":
                return
            self.run(ri, quiet=True)
            if not self.debug: self.show_faces()
        return
    
if __name__ == "__main__":
    from optparse import OptionParser

    parser = OptionParser("Usage: %prog [options] arg")
    parser.add_option("-d", "--debug", dest="debug",
                      action="store_true", default=False,
                      help="show a look while moving")
    parser.add_option("-s", "--scramble", dest="scramble",
                      action="store_true", default=False,
                      help="scramble before moving")
    parser.add_option("-b", "--batch", dest="batch",
                      default=None, help="run a batch of move notations")
    parser.add_option("-c", "--confirm", dest="confirm",
                      action="store_true", default=False,
                      help="confirm each steps")
    parser.add_option("-g", "--game", dest="game",
                      action="store_true", default=False,
                      help="enable gaming mode")
    parser.add_option("-v", "--view", dest="colors",
                      default=None, help="set each view of faces of cube in 'Right, Left, Up, Down, Front, Back' order. (ex. -v \"RRRRRRRRR|OOOOOOOOO|WWWWWWWWW|BBBBBBBBB|GGGGGGGGG|YYYYYYYYY\"")
    (options, args) = parser.parse_args()

    if (options.scramble == False) and (options.batch == None) and (options.game == False) and (options.colors == None):
        parser.print_help()
    else:
        c = Cube(debug=options.debug, colors=options.colors)
        if options.scramble:
            c.scramble()
        if options.batch:
            c.run(options.batch, options.confirm)
        c.show_faces()
        if options.game:
            c.game()


