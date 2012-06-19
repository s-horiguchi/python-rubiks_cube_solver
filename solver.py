#!/usr/bin/env python
#-*- coding:utf-8 -*-

from cube import *
from cube_def import *
from sqlalchemy import create_engine, Table, Column, MetaData, ForeignKey
from sqlalchemy import Integer, String #, Unicode, UnicodeText, DateTime
from sqlalchemy.orm import mapper, relation, sessionmaker
from sqlalchemy.ext.declarative import declarative_base ##
Base = declarative_base()

class Solution(Base):
    __tablename__ = "solutions"
    id = Column(Integer, primary_key=True)
    move_notations = Column(String(100), nullable=False, unique=True) # 100あればいいよね
    num_of_moves = Column(Integer, nullable=False)

    def __init__(self, move_notations, num_of_moves):
        self.move_notations = move_notations
        self.num_of_moves = num_of_moves
        
    def __repr__(self):
        return "<Solution(%s)>" % self.move_notations

class Position(Base):
    __tablename__ = "positions"
    # solutions を作るたびにこっちも全パターン(確定していないところはすべての組み合わせ)作る 
    #かぶってるPositionは再利用
    id = Column(Integer, primary_key=True)
    position = Column(String(500), nullable=False) # get_str_positionで取得する値にUNDEFINEDが加わる。get_str_position()は長さ481で固定っぽい

    def __init__(self, position):
        self.position = position
        
    def __repr__(self):
        return "<Position(%s)>" % self.position

class BeforeAfter(Base):
    __tablename__ = "before_after"
    # solutionsとpositionsの中間テーブル solutionsに対するある一つのpositions(before)とその(after)
    id = Column(Integer, primary_key=True)
    solution_id = Column(Integer, ForeignKey("solutions.id"))
    before_position_id = Column(Integer, ForeignKey("positions.id"))
    after_position_id = Column(Integer, ForeignKey("positions.id"))

    solution = relation("Solution")
    before_position = relation("Position", primaryjoin=before_position_id==Position.id) # 凝った
    after_position = relation("Position", primaryjoin=after_position_id==Position.id) ##
    
    def __init__(self, solution_id, before_position_id, after_position_id):
        self.solution_id = solution_id
        self.before_position_id = before_position_id
        self.after_position_id = after_position_id

    def __repr__(self):
        return "<BeforeAfter(solu=%d, before_pos=%d, after_pos=%d)>" % (self.solution_id, self.before_position_id, self.after_position_id)

class Solver(object):
    def __init__(self, debug=True):
        self.cube = Cube(debug=debug)
        # database init
        self.engine = create_engine("sqlite:///database.sqlite", echo=False, encoding="utf-8")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        
    def main(self):
        session = self.Session()
        for ba in session.query(BeforeAfter).join(Position, "before_position").filter(Position.position==self.cube.get_str_position()).all():
            print ba.solution
            print ba.before_position
            print ba.after_position
        #solu = Solution("R", 1)
        #pos1 = Position("0,-1,1,2,-1,-1,5|1,-1,-1,2,-1,-1,5|2,0,-1,2,-1,-1,5|3,-1,1,2,-1,-1,-1|4,-1,-1,2,-1,-1,-1|5,0,-1,2,-1,-1,-1|6,-1,1,2,-1,4,-1|7,-1,-1,2,-1,4,-1|8,0,-1,2,-1,4,-1|9,-1,1,-1,-1,-1,5|10,-1,-1,-1,-1,-1,5|11,0,-1,-1,-1,-1,5|12,-1,1,-1,-1,-1,-1|13,0,-1,-1,-1,-1,-1|14,-1,1,-1,-1,4,-1|15,-1,-1,-1,-1,4,-1|16,0,-1,-1,-1,4,-1|17,-1,1,-1,3,-1,5|18,-1,-1,-1,3,-1,5|19,0,-1,-1,3,-1,5|20,-1,1,-1,3,-1,-1|21,-1,-1,-1,3,-1,-1|22,0,-1,-1,3,-1,-1|23,-1,1,-1,3,4,-1|24,-1,-1,-1,3,4,-1|25,0,-1,-1,3,4,-1")
        #pos2 = Position("0,-1,1,2,-1,-1,5|1,-1,-1,2,-1,-1,5|8,0,-1,4,-1,-1,2|3,-1,1,2,-1,-1,-1|4,-1,-1,2,-1,-1,-1|16,0,-1,4,-1,-1,-1|6,-1,1,2,-1,4,-1|7,-1,-1,2,-1,4,-1|25,0,-1,4,-1,3,-1|9,-1,1,-1,-1,-1,5|10,-1,-1,-1,-1,-1,5|5,0,-1,-1,-1,-1,2|12,-1,1,-1,-1,-1,-1|13,0,-1,-1,-1,-1,-1|14,-1,1,-1,-1,4,-1|15,-1,-1,-1,-1,4,-1|22,0,-1,-1,-1,3,-1|17,-1,1,-1,3,-1,5|18,-1,-1,-1,3,-1,5|2,0,-1,-1,5,-1,2|20,-1,1,-1,3,-1,-1|21,-1,-1,-1,3,-1,-1|11,0,-1,-1,5,-1,-1|23,-1,1,-1,3,4,-1|24,-1,-1,-1,3,4,-1|19,0,-1,-1,5,3,-1")
        #session.add_all([solu, pos1, pos2])
        #session.commit()
        #ba = BeforeAfter(solu.id, pos1.id, pos2.id)
        #session.add(ba)
        #session.commit()
        session.close()
        return
        
    def step1(cube, start_face=BLUE):
        # 底面十字
        cube.get_face_by_center_color(start_face)
        
if __name__ == "__main__":
    s = Solver()
    s.main()
