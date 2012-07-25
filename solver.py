#! /usr/bin/env python
#-*- coding: utf-8 -*-

from cube import *
from cube_def import *
from sqlalchemy import create_engine, Column, ForeignKey
from sqlalchemy import Integer, String
from sqlalchemy.orm import relation, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import itertools
import datetime
Base = declarative_base()


class Solution(Base):
    __tablename__ = "solutions"
    id = Column(Integer, primary_key=True)
    move_notations = Column(String(100), nullable=False, unique=True) # is 100 enough ?
    num_of_moves = Column(Integer, nullable=False)

    def __init__(self, move_notations, num_of_moves):
        self.move_notations = move_notations
        self.num_of_moves = num_of_moves
        
    def __repr__(self):
        return "<Solution(%s)>" % self.move_notations

class PieceMove(Base):
    __tablename__ = "piece_move"
    # for move only 1 piece to specified location
    id = Column(Integer, primary_key=True)
    before_location = Column(Integer, nullable=False)
    after_location = Column(Integer, nullable=False)
    solution_id = Column(Integer, ForeignKey("solutions.id"))
    solution = relation("Solution")
    
    def __init__(self, before_location, after_location, solution_id):
        self.before_location = before_location
        self.after_location = after_location
        self.solution_id = solution_id

    def __repr__(self):
        return "<PieceMove(%d, before_loc=%d, after_loc=%d, solu=%d)>" % (self.id, self.before_location, self.after_location, self.solution_id)

class Solver(object):
    def __init__(self, debug=True, str_position=None, colors=None):
        self.cube = Cube(debug=debug, str_position=str_position, colors=colors)
        self.debug = debug
        #self.goal = "0,-1,1,2,-1,-1,5|1,-1,-1,2,-1,-1,5|2,0,-1,2,-1,-1,5|3,-1,1,2,-1,-1,-1|4,-1,-1,2,-1,-1,-1|5,0,-1,2,-1,-1,-1|6,-1,1,2,-1,4,-1|7,-1,-1,2,-1,4,-1|8,0,-1,2,-1,4,-1|9,-1,1,-1,-1,-1,5|10,-1,-1,-1,-1,-1,5|11,0,-1,-1,-1,-1,5|12,-1,1,-1,-1,-1,-1|13,0,-1,-1,-1,-1,-1|14,-1,1,-1,-1,4,-1|15,-1,-1,-1,-1,4,-1|16,0,-1,-1,-1,4,-1|17,-1,1,-1,3,-1,5|18,-1,-1,-1,3,-1,5|19,0,-1,-1,3,-1,5|20,-1,1,-1,3,-1,-1|21,-1,-1,-1,3,-1,-1|22,0,-1,-1,3,-1,-1|23,-1,1,-1,3,4,-1|24,-1,-1,-1,3,4,-1|25,0,-1,-1,3,4,-1"
        # database init
        self.engine = create_engine("sqlite:///database.sqlite", echo=debug, encoding="utf-8")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def lbl_run(self):
        start_time = datetime.datetime.now()
        session = self.Session()
        self.solution = ""
        self.num_of_moves = 0
        
        self.cube.show_faces()
        print "<stage 1>  Cross on [Down]"
        for piece_num, after_loc in [(18, L_DB), (20, L_DL), (22, L_DR), (24, L_DF)]: # BY, BO, BR, BG
            for num_loc, piece in enumerate(self.cube.pieces):
                if piece.num == piece_num:
                    piece.get_rotate_to_be(PIECES[piece_num])
                    q = session.query(PieceMove).filter((PieceMove.before_location == num_loc) and (PieceMove.after_location == after_loc))
                    if q.count() < 1:
                        print "[*] Database is not completed"
                        session.close()
                        return
                    else:
                        pm = q.first()
                        self.solution += pm.solution.move_notations
                        self.cube.run(pm.solution.move_notations, confirm=False, quiet=True)
                        self.num_of_moves += pm.solution.num_of_moves
        self.cube.show_faces()

        delta = datetime.datetime.now() - self.start_time
        print "Running time: %ddays %dh:%dm:%d.%ds" % (delta.days, delta.seconds / 3600, (delta.seconds % 3600) / 60, (delta.seconds % 3600) % 60, delta.microseconds)
        print 
        session.close()
        return

    
if __name__ == "__main__":
    from optparse import OptionParser

    parser = OptionParser("Usage: %prog [options] FACE_VIEWS")
    parser.add_option("-s", "--solve", dest="solve",
                      action="store_true", default=False,
                      help="enable solving mode")
    parser.add_option("-d", "--debug", dest="debug",
                      action="store_true", default=False,
                      help="enable debug mode")
    (options, args) = parser.parse_args()

    if len(args) > 0:
        if options.solve:
            s = Solver(colors=args[0], debug=options.debug)
            s.lbl_run()
        else:
            parser.print_help()
    else: # there's no FACE_VIEW
        parser.print_help()
