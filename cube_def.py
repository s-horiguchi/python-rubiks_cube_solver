#!/usr/bin/env python
#-*- coding:utf-8 -*-

       
#                          ___ ___ ___
#                        /___/___/___/|
#                       /___/_U_/___/||
#                      /___/___/__ /|/|
#                     |   |   |   | /|| 
#                     |___|___|___|/R/|
#                     |   | F |   | /||
#                     |___|___|___|/|/
#                     |   |   |   | /
#                     |___|___|___|/ 

# face sign
NONE = -1 # キューブの表面に出ない面
UNDEFINED = -2 # 未確定　動かしても良い for solver
#DEFINED = -3 # 確定済み　動かしてはいけない for solver
# face color
RED = 0   #B
ORANGE = 1    #R
WHITE = 2 #Y
BLUE = 3 #O
GREEN = 4  #G
YELLOW = 5  #W
COLOR = ["R", "O", "W", "B", "G", "Y"]

Right = 0
Left = 1
Up = 2
#Bottom = 3
Down = 3
Front = 4
Back =5
FACE = ["Right", "Left", "Up", "Down", "Front", "Back"]

PIECES = [
    [NONE, ORANGE, WHITE, NONE, NONE, YELLOW], # WOY
    [NONE, NONE, WHITE, NONE, NONE, YELLOW], # WY
    [RED, NONE, WHITE, NONE, NONE, YELLOW], # WRY
    [NONE, ORANGE, WHITE, NONE, NONE, NONE], # WO
    [NONE, NONE, WHITE, NONE, NONE, NONE], # W
    [RED, NONE, WHITE, NONE, NONE, NONE], # WR
    [NONE, ORANGE, WHITE, NONE, GREEN, NONE], # WOG
    [NONE, NONE, WHITE, NONE, GREEN, NONE], # WG
    [RED, NONE, WHITE, NONE, GREEN, NONE], # WRG
    [NONE, ORANGE, NONE, NONE, NONE, YELLOW], # OY
    [NONE, NONE, NONE, NONE, NONE, YELLOW], # Y
    [RED, NONE, NONE, NONE, NONE, YELLOW], # RY
    [NONE, ORANGE, NONE, NONE, NONE, NONE], # O
    [RED, NONE, NONE, NONE, NONE, NONE], # R
    [NONE, ORANGE, NONE, NONE, GREEN, NONE], # OG
    [NONE, NONE, NONE, NONE, GREEN, NONE], # G
    [RED, NONE, NONE, NONE, GREEN, NONE], # RG
    [NONE, ORANGE, NONE, BLUE, NONE, YELLOW], # BOY
    [NONE, NONE, NONE, BLUE, NONE, YELLOW], # BY
    [RED, NONE, NONE, BLUE, NONE, YELLOW], # BRY
    [NONE, ORANGE, NONE, BLUE, NONE, NONE], # BO
    [NONE, NONE, NONE, BLUE, NONE, NONE], # B
    [RED, NONE, NONE, BLUE, NONE, NONE], # BR
    [NONE, ORANGE, NONE, BLUE, GREEN, NONE], # BOG
    [NONE, NONE, NONE, BLUE, GREEN, NONE], # BG
    [RED, NONE, NONE, BLUE, GREEN, NONE], # BRG
    ]

L_ULB = 0
L_UB = 1
L_URB = 2
L_UL = 3
L_U = 4
L_UR = 5
L_ULF = 6
L_UF = 7
L_URF = 8
L_LB = 9
L_B = 10
L_RB = 11
L_L = 12
L_R = 13
L_LF = 14
L_F = 15
L_RF = 16
L_DLB = 17
L_DB = 18
L_DRB = 19
L_DL = 20
L_D = 21
L_DR = 22
L_DLF = 23
L_DF = 24
L_DRF = 25

NUM_SCRAMBLE_MOVES = 25

ROTATE_WAYS = ["R", "R'", "R2", "L", "L'", "L2", "U", "U'", "U2", "D", "D'", "D2", "F", "F'", "F2", "B", "B'", "B2", "M", "M'", "M2"]
SINGLE_ROTATE_WAYS = ["R", "L", "U", "D", "F", "B", "M"]
