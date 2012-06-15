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

# colors
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
Bottom = 3
Front = 4
Back =5
FACE = ["Right", "Left", "Up", "Bottom", "Front", "Back"]

PIECES = [
    [None, ORANGE, WHITE, None, None, YELLOW], # WOY
    [None, None, WHITE, None, None, YELLOW], # WY
    [RED, None, WHITE, None, None, YELLOW], # WRY
    [None, ORANGE, WHITE, None, None, None], # WO
    [None, None, WHITE, None, None, None], # W
    [RED, None, WHITE, None, None, None], # WR
    [None, ORANGE, WHITE, None, GREEN, None], # WOG
    [None, None, WHITE, None, GREEN, None], # WG
    [RED, None, WHITE, None, GREEN, None], # WRG
    [None, ORANGE, None, None, None, YELLOW], # OY
    [None, None, None, None, None, YELLOW], # Y
    [RED, None, None, None, None, YELLOW], # RY
    [None, ORANGE, None, None, None, None], # O
    [RED, None, None, None, None, None], # R
    [None, ORANGE, None, None, GREEN, None], # OG
    [None, None, None, None, GREEN, None], # G
    [RED, None, None, None, GREEN, None], # RG
    [None, ORANGE, None, BLUE, None, YELLOW], # BOY
    [None, None, None, BLUE, None, YELLOW], # BY
    [RED, None, None, BLUE, None, YELLOW], # BRY
    [None, ORANGE, None, BLUE, None, None], # BO
    [None, None, None, BLUE, None, None], # B
    [RED, None, None, BLUE, None, None], # BR
    [None, ORANGE, None, BLUE, GREEN, None], # BOG
    [None, None, None, BLUE, GREEN, None], # BG
    [RED, None, None, BLUE, GREEN, None], # BRG
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

ROTATE_WAYS = ["R", "R'", "R2", "L", "L'", "L2", "U", "U'", "U2", "D", "D'", "D2", "F", "F'", "F2", "B", "B'", "B2"]
#ROTATE_WAYS = ["R", "R'", "L", "L'", "U", "U'", "D", "D'", "F", "F'", "B", "B'"]
