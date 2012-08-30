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
DEFINED = -3 # 確定済み　動かしてはいけない for solver
# face color
RED = 0   #B
ORANGE = 1    #R
WHITE = 2 #Y
BLUE = 3 #O
GREEN = 4  #G
YELLOW = 5  #W
COLOR = ["R", "O", "W", "B", "G", "Y", "D", "U", "N"]
FACELETS = ["R", "L", "U", "D", "F", "B"]

Right = 0
Left = 1
Up = 2
#Bottom = 3
Down = 3
Front = 4
Back =5
FACE = ["Right", "Left", "Up", "Down", "Front", "Back"]

PIECES = [
    (NONE, ORANGE, WHITE, NONE, NONE, YELLOW), # WOY
    (NONE, NONE, WHITE, NONE, NONE, YELLOW), # WY
    (RED, NONE, WHITE, NONE, NONE, YELLOW), # WRY
    (NONE, ORANGE, WHITE, NONE, NONE, NONE), # WO
    (NONE, NONE, WHITE, NONE, NONE, NONE), # W
    (RED, NONE, WHITE, NONE, NONE, NONE), # WR
    (NONE, ORANGE, WHITE, NONE, GREEN, NONE), # WOG
    (NONE, NONE, WHITE, NONE, GREEN, NONE), # WG
    (RED, NONE, WHITE, NONE, GREEN, NONE), # WRG
    (NONE, ORANGE, NONE, NONE, NONE, YELLOW), # OY
    (NONE, NONE, NONE, NONE, NONE, YELLOW), # Y
    (RED, NONE, NONE, NONE, NONE, YELLOW), # RY
    (NONE, ORANGE, NONE, NONE, NONE, NONE), # O
    (RED, NONE, NONE, NONE, NONE, NONE), # R
    (NONE, ORANGE, NONE, NONE, GREEN, NONE), # OG
    (NONE, NONE, NONE, NONE, GREEN, NONE), # G
    (RED, NONE, NONE, NONE, GREEN, NONE), # RG
    (NONE, ORANGE, NONE, BLUE, NONE, YELLOW), # BOY
    (NONE, NONE, NONE, BLUE, NONE, YELLOW), # BY
    (RED, NONE, NONE, BLUE, NONE, YELLOW), # BRY
    (NONE, ORANGE, NONE, BLUE, NONE, NONE), # BO
    (NONE, NONE, NONE, BLUE, NONE, NONE), # B
    (RED, NONE, NONE, BLUE, NONE, NONE), # BR
    (NONE, ORANGE, NONE, BLUE, GREEN, NONE), # BOG
    (NONE, NONE, NONE, BLUE, GREEN, NONE), # BG
    (RED, NONE, NONE, BLUE, GREEN, NONE), # BRG
    ]
PIECES_without_NONE = [[e for e in p if e != NONE] for p in PIECES]

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

LOCATION = [((Up, 0), (Left, 0), (Back, 2)),
            ((Up, 1), (Back, 1)),
            ((Up, 2), (Right, 2), (Back, 0)),
            ((Up, 3), (Left, 1)),
            ((Up, 4), ),
            ((Up, 5), (Right, 1)),
            ((Up, 6), (Left, 2), (Front, 0)),
            ((Up, 7), (Front, 1)),
            ((Up, 8), (Right, 0), (Front, 2)),
            ((Left, 3), (Back, 5)),
            ((Back, 4), ),
            ((Right, 5), (Back, 3)),
            ((Left, 4), ),
            ((Right, 4), ),
            ((Left, 5), (Front, 3)),
            ((Front, 4), ),
            ((Right, 3), (Front, 5)),
            ((Down, 6), (Left, 6), (Back, 8)),
            ((Down, 7), (Back, 7)),
            ((Down, 8), (Right, 8), (Back, 6)),
            ((Down, 3), (Left, 7)),
            ((Down, 4), ),
            ((Down, 5), (Right, 7)),
            ((Down, 0), (Left, 8), (Front, 6)),
            ((Down, 1), (Front, 7)),
            ((Down, 2), (Right, 6), (Front, 8))
            ]
NUM_SCRAMBLE_MOVES = 25

ALL_ROTATE_WAYS = ["R", "R'", "R2", "L", "L'", "L2", "U", "U'", "U2", "D", "D'", "D2", "F", "F'", "F2", "B", "B'", "B2", "M", "M'", "M2", "E", "E'", "E2", "S", "S'", "S2", "(r)", "(r')", "(r2)", "(f)", "(f')", "(f2)", "(u)", "(u')", "(u2)"]
ROTATE_WAYS = ["R", "R'", "R2", "L", "L'", "L2", "U", "U'", "U2", "D", "D'", "D2", "F", "F'", "F2", "B", "B'", "B2"]
SINGLE_ROTATE_WAYS = ["R", "L", "U", "D", "F", "B", "M", "E", "S"]
ENTIRE_ROTATE_WAYS = ["(r)", "(r')", "(r2)", "(f)", "(f')", "(f2)", "(u)", "(u')", "(u2)"]
ENTIRE_ROTATE_WATS_short = ["(r)", "(f)", "(u)"]
ENTIRE_ROTATE_WAYS_simple = ["r", "f", "u"]

TRANSLATION_MAP = [ # which notation each one in ALL_ROTATE_WAYS translate to
    # (up, donw) = (WHITE, BLUE)

    ["R", "R'", "R2", "L", "L'", "L2", "U", "U'", "U2", "D", "D'", "D2", "F", "F'", "F2", "B", "B'", "B2", ], #"M", "M'", "M2", "E", "E'", "E2", "S", "S'", "S2", "(r)", "(r')", "(f)", "(f')", "(u)" ,"(u')"],     # this position is standard
    ["B", "B'", "B2", "F", "F'", "F2", "U", "U'", "U2", "D", "D'", "D2", "R", "R'", "R2", "L", "L'", "L2", ], #"S", "S'", "S2", "E", "E'", "E2", "M'", "M", "M2", "(f')", "(f)", "(r)", "(r')", "(u)", "(u')"],
    ["L", "L'", "L2", "R", "R'", "R2", "U", "U'", "U2", "D", "D'", "D2", "B", "B'", "B2", "F", "F'", "F2", ], #"M'", "M", "M2", "E", "E'", "E2", "S'", "S", "S2", "(r')", "(r)", "(f)", "(f')", "(u')", "(u)"],
    ["F", "F'", "F2", "B", "B'", "B2", "U", "U'", "U2", "D", "D'", "D2", "L", "L'", "L2", "R", "R'", "R2", ], #"S'", "S", "S2", "E", "E'", "E2", "M", "M'", "M2", "(f)", "(f')", "(r')", "(r)", "(u)", "(u')"],
    # (GREEN, YELLOW)
    ["R", "R'", "R2", "L", "L'", "L2", "B", "B'", "B2", "F", "F'", "F2", "U", "U'", "U2", "D", "D'", "D2", ], #"M", "M'", "M2", "S", "S'", "S2", "E'", "E", "E2", "(r)", "(r')", "(u)", "(u')", "(f')", "(f)"],
    ["B", "B'", "B2", "F", "F'", "F2", "L", "L'", "L2", "R", "R'", "R2", "U", "U'", "U2", "D", "D'", "D2", ], #"S", "S'", "S2", "M'", "M", "M2", "E'", "E", "E2", "(f')", "(f)", "(u)", "(u')", "(r')", "(r)"],
    ["L", "L'", "L2", "R", "R'", "R2", "F", "F'", "F2", "B", "B'", "B2", "U", "U'", "U2", "D", "D'", "D2", ], #"M'", "M", "M2", "S'", "S", "S2", "E'", "E", "E2"],
    ["F", "F'", "F2", "B", "B'", "B2", "R", "R'", "R2", "L", "L'", "L2", "U", "U'", "U2", "D", "D'", "D2", ], #"S'", "S", "S2", "M", "M'", "M2", "E'", "E", "E2"],
    # (BLUE, WHITE)
    ["R", "R'", "R2", "L", "L'", "L2", "D", "D'", "D2", "U", "U'", "U2", "B", "B'", "B2", "F", "F'", "F2", ],
    ["B", "B'", "B2", "F", "F'", "F2", "D", "D'", "D2", "U", "U'", "U2", "L", "L'", "L2", "R", "R'", "R2", ],
    ["L", "L'", "L2", "R", "R'", "R2", "D", "D'", "D2", "U", "U'", "U2", "F", "F'", "F2", "B", "B'", "B2", ],
    ["F", "F'", "F2", "B", "B'", "B2", "D", "D'", "D2", "U", "U'", "U2", "R", "R'", "R2", "L", "L'", "L2", ],
    # (YELLOW, GREEN)
    ["R", "R'", "R2", "L", "L'", "L2", "F", "F'", "F2", "B", "B'", "B2", "D", "D'", "D2", "U", "U'", "U2", ],
    ["B", "B'", "B2", "F", "F'", "F2", "R", "R'", "R2", "L", "L'", "L2", "D", "D'", "D2", "U", "U'", "U2", ],
    ["L", "L'", "L2", "R", "R'", "R2", "B", "B'", "B2", "F", "F'", "F2", "D", "D'", "D2", "U", "U'", "U2", ],
    ["F", "F'", "F2", "B", "B'", "B2", "L", "L'", "L2", "R", "R'", "R2", "D", "D'", "D2", "U", "U'", "U2", ],
    # (RED, ORANGE)
    ["U", "U'", "U2", "D", "D'", "D2", "L", "L'", "L2", "R", "R'", "R2", "F", "F'", "F2", "B", "B'", "B2", ],
    ["L", "L'", "L2", "R", "R'", "R2", "D", "D'", "D2", "U", "U'", "U2", "F", "F'", "F2", "B", "B'", "B2", ],
    ["D", "D'", "D2", "U", "U'", "U2", "R", "R'", "R2", "L", "L'", "L2", "F", "F'", "F2", "B", "B'", "B2", ],
    ["R", "R'", "R2", "L", "L'", "L2", "U", "U'", "U2", "D", "D'", "D2", "F", "F'", "F2", "B", "B'", "B2", ],
    # (ORANGE, RED)
    ["D", "D'", "D2", "U", "U'", "U2", "R", "R'", "R2", "L", "L'", "L2", "F", "F'", "F2", "B", "B'", "B2", ],
    ["R", "R'", "R2", "L", "L'", "L2", "U", "U'", "U2", "D", "D'", "D2", "F", "F'", "F2", "B", "B'", "B2", ],
    ["U", "U'", "U2", "D", "D'", "D2", "L", "L'", "L2", "R", "R'", "R2", "F", "F'", "F2", "B", "B'", "B2", ],
    ["L", "L'", "L2", "R", "R'", "R2", "D", "D'", "D2", "U", "U'", "U2", "F", "F'", "F2", "B", "B'", "B2", ],
    ]

ROTATED_CENTER_COLORS = [
    # colors of center of the cube
    # (up, donw) = (WHITE, BLUE)
    [RED, ORANGE, WHITE, BLUE, GREEN, YELLOW], #0 # this is standard position
    [GREEN, YELLOW, WHITE, BLUE, ORANGE, RED], #1
    [ORANGE, RED, WHITE, BLUE, YELLOW, GREEN], #2
    [YELLOW, GREEN, WHITE, BLUE, RED, ORANGE], #3
    # (GREEN, YELLOW)
    [RED, ORANGE, GREEN, YELLOW, BLUE, WHITE], #4
    [BLUE, WHITE, GREEN, YELLOW, ORANGE, RED], #5
    [ORANGE, RED, GREEN, YELLOW, WHITE, BLUE], #6
    [WHITE, BLUE, GREEN, YELLOW, RED, ORANGE], #7
    # (BLUE, WHITE)
    [RED, ORANGE, BLUE, WHITE, YELLOW, GREEN], #8
    [YELLOW, GREEN, BLUE, WHITE, ORANGE, RED], #9
    [ORANGE, RED, BLUE, WHITE, GREEN, YELLOW], #10
    [GREEN, YELLOW, BLUE, WHITE, RED, ORANGE], #11
    # (YELLOW, GREEN)
    [RED, ORANGE, YELLOW, GREEN, WHITE, BLUE], #12
    [WHITE, BLUE, YELLOW, GREEN, ORANGE, RED], #13
    [ORANGE, RED, YELLOW, GREEN, BLUE, WHITE], #14
    [BLUE, WHITE, YELLOW, GREEN, RED, ORANGE], #15
    # (RED, ORANGE)
    [GREEN, YELLOW, RED, ORANGE, WHITE, BLUE], #16
    [WHITE, BLUE, RED, ORANGE, YELLOW, GREEN], #17
    [YELLOW, GREEN, RED, ORANGE, BLUE, WHITE], #18
    [BLUE, WHITE, RED, ORANGE, GREEN, YELLOW], #19
    # (ORANGE, RED)
    [GREEN, YELLOW, ORANGE, RED, BLUE, WHITE], #20
    [BLUE, WHITE, ORANGE, RED, YELLOW, GREEN], #21
    [YELLOW, GREEN, ORANGE, RED, WHITE, BLUE], #22
    [WHITE, BLUE, ORANGE, RED, GREEN, YELLOW], #23
    ]
