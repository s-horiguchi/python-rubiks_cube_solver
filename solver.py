#!/usr/bin/env python
#-*- coding:utf-8 -*-

from cube import *
from cube_def import *
from sqlalchemy import create_engine, Column, ForeignKey
from sqlalchemy import Integer, String
from sqlalchemy.orm import relation, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import itertools
import datetime
Base = declarative_base()

STAGE_LIST = [(5, ""), # Cross on Down + Center on (Right, Left, Front, Back)
              (4, ""), # All on Down
              (8, ""), # Down and 2 step from Down on (Right, Left, Front, Back)
              (4, ""), # Cross on Up
              

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
    # すべてget_str_position(standard=True)で保存

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
        return "<BeforeAfter(%d, solu=%d, before_pos=%d, after_pos=%d)>" % (self.id, self.solution_id, self.before_position_id, self.after_position_id)

class Solver(object):
    def __init__(self, debug=True, str_position=None, colors=None, is_first=False):
        self.cube = Cube(debug=debug, str_position=str_position, colors=colors)
        self.debug = debug
        # database init
        self.engine = create_engine("sqlite:///database.sqlite", echo=False, encoding="utf-8")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.goal = "0,-1,1,2,-1,-1,5|1,-1,-1,2,-1,-1,5|2,0,-1,2,-1,-1,5|3,-1,1,2,-1,-1,-1|4,-1,-1,2,-1,-1,-1|5,0,-1,2,-1,-1,-1|6,-1,1,2,-1,4,-1|7,-1,-1,2,-1,4,-1|8,0,-1,2,-1,4,-1|9,-1,1,-1,-1,-1,5|10,-1,-1,-1,-1,-1,5|11,0,-1,-1,-1,-1,5|12,-1,1,-1,-1,-1,-1|13,0,-1,-1,-1,-1,-1|14,-1,1,-1,-1,4,-1|15,-1,-1,-1,-1,4,-1|16,0,-1,-1,-1,4,-1|17,-1,1,-1,3,-1,5|18,-1,-1,-1,3,-1,5|19,0,-1,-1,3,-1,5|20,-1,1,-1,3,-1,-1|21,-1,-1,-1,3,-1,-1|22,0,-1,-1,3,-1,-1|23,-1,1,-1,3,4,-1|24,-1,-1,-1,3,4,-1|25,0,-1,-1,3,4,-1"
        self.is_first = is_first
        
    def main(self):
        self.start_time = datetime.datetime.now()
        if self.debug:
            print "[*] normal"
            self.cube.show_faces(standard=False)
            print "[*] standard"
            self.cube.show_faces(standard=True)
        
        self.first_position = self.cube.get_str_position(standard=True)
        
        self.solution = (None, 1000) # self.solution[1] is enough big ?

        for max_depth, goal in STAGE_LIST:
            self.run_stage(max_depth, goal)
            

        if self.solution[0]:
            print "[*] Solution Found:"
            print "shortest one:", self.solution[0]
            print "length:", self.solution[1]
        else:
            print "[*] couldn't find!!"
        print 
        delta = datetime.datetime.now() - self.start_time
        print "Running time: %ddays %dh:%dm:%d.%ds" % (delta.days, delta.seconds / 3600, (delta.seconds % 3600) / 60, (delta.seconds % 3600) % 60, delta.microseconds)
        print 
        return
        
    def run_stage(self, cur_max_depth, cur_goal):
        self.max_depth = cur_max_depth
        self.cur_goal = cur_goal
        self.loop([], self.first_position)

        return

    def loop(self, cur_depth, pos):
        print "-- loop() @", [baid for baid, p in cur_depth]
        # cur_depth = [((BeforeAfter.id, ), before_position), (...), ...]
        # pos = after_position
        session = self.Session()
        ba_cand = []
        for ba in session.query(BeforeAfter).join(Position, "before_position").filter(Position.position==pos).all(): ## tricky
            ba_cand.append((ba, ""))
        self.cube.set_str_position(self.first_position) # reset cube to first_position
        self.cube.run("".join([ba[1]+session.query(BeforeAfter).get(ba[0]).solution.move_notations for ba, p in cur_depth]), confirm=False, quiet=True) # store position in this routine
        stored_position = self.cube.get_str_position(standard=False)
        print "< stored_pos ( %s )>" % "".join([ba[1]+session.query(BeforeAfter).get(ba[0]).solution.move_notations for ba, p in cur_depth]), 
        self.cube.show_faces(standard=True)
        for w in ENTIRE_ROTATE_WAYS: # will be ALL_ROTATE_WAYS
            self.cube.run(w, confirm=False, quiet=True)
            #print "<", w, ">", 
            #self.cube.show_faces(standard=True)
            for ba in session.query(BeforeAfter).join(Position, "before_position").filter(Position.position==self.cube.get_str_position(standard=True)).all():
                ba_cand.append((ba, w))
            self.cube.set_str_position(stored_position) # restore
        ret = []
        print ba_cand
        for ba in ba_cand:
            if ba[1]:
                print "[*] with rotate", ba[1]
            if ba[0].after_position.position == self.cur_goal:
                print "[*] Found! @", [baid for baid, p in cur_depth]
                ret.append((ba[1] + ba[0].solution.move_notations, 1 + ba[0].solution.num_of_moves))
            else:
                if (True in [ba[0].after_position.position == p for baid, p in cur_depth]) or (ba[0].after_position.position == self.first_position):
                    print "looping :-("
                elif len(cur_depth) > self.max_depth:
                    print "too long branch X("
                else:
                    print "new branch :P"
                    ret_ = self.loop(cur_depth+[((ba[0].id, ba[1]), pos)], ba[0].after_position.position)
                    print "-- loop() @", [baid for baid, p in cur_depth]
                    if ret_: # found solution
                        if ba[1]:
                            [ret.append((ba[1] + ba[0].solution.move_notations + r[0], 1 + r[1] + ba[0].solution.num_of_moves)) for r in ret_ if r[1] < self.solution[1]]
                        else:
                            [ret.append((ba[0].solution.move_notations + r[0], r[1] + ba[0].solution.num_of_moves)) for r in ret_ if r[1] < self.solution[1]]
        if ret == []: # dead branch
            # to clear up
            print "dead branch :-C"
            ret = False
        else: # in solution branch
            if cur_depth == []: # really final step
                for r in ret:
                    if self.solution[1] > r[1]:
                        self.solution = r

        session.close()
        return ret
        
    def add_data(self, batch, colors):
        # colors: ex.)"URRURRRRR|OOUOOUOOO|WWWWWWUUU|BUBBBBBBB|GGGGGGGGG|YYYYYYYYY"
        # "U" = UNDEFINED
        undefined = []
        unused_colors = [9, 9, 9, 9, 9, 9] # for R,L,U,D,F,B
        faces_colors = [[None, None, None, None, None, None, None, None, None], [None, None, None, None, None, None, None, None, None], [None, None, None, None, None, None, None, None, None], [None, None, None, None, None, None, None, None, None], [None, None, None, None, None, None, None, None, None], [None, None, None, None, None, None, None, None, None]] #[[None]*9]*6
        for i1, f in enumerate(colors.split("|")):
            for i2, c in enumerate(f):
                if c == "U":  # UNDEFINED
                    undefined.append((i1, i2))
                elif c in COLOR[:-3]: # DEFINED
                    i = COLOR.index(c)
                    unused_colors[i] -= 1
                    faces_colors[i1][i2] = i
                    #raw_input()
                else:
                    print "[*] invalid FACE_VIEWS including 'UNDEFINED'!"
                    raise
        unused_ncolor = []
        for i, c in enumerate(unused_colors):
            for x in xrange(c):
                unused_ncolor.append(i)

        assert len(unused_ncolor) == len(undefined)
        counter = 0
        
        for perm in itertools.permutations(unused_ncolor):
            for i,p in zip(undefined, perm):
                faces_colors[i[0]][i[1]] = p
            if not self.cube.set_by_faces_color(faces_colors, quiet=True):
                continue
            else:
                self.update_db(batch)
                counter += 1
        print
        print "[*] Finish!"
        print "[*] total number of patterns:", counter
        return

    def update_db(self, batch):
        session = self.Session()
        # before position
        p = self.cube.get_str_position(standard=True)
        print p
        query = session.query(Position).filter(Position.position==p)
        if p == self.goal:
            print "[*] already finished solution"
            return

        if query.count() > 0:
            before_pos = query.first()
            if not self.is_first and session.query(BeforeAfter).filter(BeforeAfter.before_position==before_pos).count() > 0:
                print "[*] better solution is already available."
                print "[*] so prevent create new BeforeAfter and return."
                return
        else:
            before_pos = Position(position=p)
            session.add(before_pos)
            session.commit()
            
        print "[*] before"
        
        before_colors = self.cube.show_faces(standard=False)
        num_of_moves = self.cube.run(batch, quiet=False) ## run
        print "[*] after"
        after_colors = self.cube.show_faces(standard=False)
        # solution
        query = session.query(Solution).filter(Solution.move_notations==batch)
        if query.count() > 0:
            solu = query.first()
        else:
            solu = Solution(move_notations=batch, num_of_moves=num_of_moves)
            session.add(solu)
            session.commit()
        # after position
        p = self.cube.get_str_position(standard=True)
        print p
        query = session.query(Position).filter(Position.position==p)
        if query.count() > 0:
            after_pos = query.first()
        else:
            after_pos = Position(position=p)
            session.add(after_pos)
            session.commit()
        # before after
        query = session.query(BeforeAfter).filter(BeforeAfter.solution_id==solu.id).filter(BeforeAfter.before_position_id==before_pos.id).filter(BeforeAfter.after_position_id==after_pos.id)
        if query.count() > 0:
            pass
        else:
            ba = BeforeAfter(solution_id=solu.id, before_position_id=before_pos.id, after_position_id=after_pos.id)
            session.add(ba)
            session.commit()
        
        session.close()
        return

    def check_positions_in_db(self, pid=None):
        session = self.Session()
        query = session.query(Position)
        if pid:
            query = query.filter(Position.id == pid)
        for pos in query.all():
            print "[*] <Position(%d)>" % pos.id
            self.cube.set_str_position(pos.position)
            self.cube.show_faces(standard=False) # whichever
            print
        session.close()
        return
        
    def clear_db(self):
        Base.metadata.drop_all(self.engine)
        return
    
if __name__ == "__main__":
    from optparse import OptionParser

    parser = OptionParser("Usage: %prog [options] FACE_VIEWS")
    parser.add_option("-a", "--add", dest="add", metavar="BATCH",
                      default=None, help="add data after running a batch of move notations")
    parser.add_option("-s", "--solve", dest="solve",
                      action="store_true", default=False,
                      help="enable solving mode")
    parser.add_option("-d", "--debug", dest="debug",
                      action="store_true", default=False,
                      help="enable debug mode")
    parser.add_option("-p", "--check_position", dest="checkp",
                      action="store_true", default=False,
                      help="check positions in database (for debug)")
    parser.add_option("-c", "--clar_db", dest="clear_db",
                      action="store_true", default=False,
                      help="clear all data from database")
    parser.add_option("-f", "--is_first", dest="is_first",
                      action="store_true", default=False,
                      help="\"is first?\" flag")
    (options, args) = parser.parse_args()

    if len(args) > 0:
        if options.add:
            s = Solver(debug=options.debug, is_first=options.is_first)
            s.add_data(options.add, colors=args[0])
        elif options.solve:
            s = Solver(colors=args[0], debug=options.debug, is_first=options.is_first)
            s.main()
        elif options.checkp:
            s = Solver(is_first=options.is_first)
            s.check_positions_in_db(pid=args[0])
        else:
            parser.print_help()
    else: # there's no FACE_VIEW
        if options.checkp:
            s = Solver(is_first=options.is_first)
            s.check_positions_in_db()
        elif options.clear_db:
            s = Solver(is_first=options.is_first)
            s.clear_db()
        else:
            parser.print_help()
