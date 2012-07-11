#!/usr/bin/env python
#-*- coding:utf-8 -*-

from cube import *
from cube_def import *
from sqlalchemy import create_engine, Column, ForeignKey
from sqlalchemy import Integer, String
from sqlalchemy.orm import relation, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import itertools
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
        return "<BeforeAfter(solu=%d, before_pos=%d, after_pos=%d)>" % (self.solution_id, self.before_position_id, self.after_position_id)

def get_value_from_dict_by_key_str(d, s):
    ret = d
    if s:
        for k in s.split("."):
            if k != "":
                ret = ret.get(k)
            
    return ret


def del_item_from_dict_by_key_str(d, s):
    print "[*] @del", d,s
    if s:
        d2 = get_value_from_dict_by_key_str(d, ".".join(s.split(".")[:-1]))
        d2.pop(s.split(".")[-1])
    return

class Solver(object):
    def __init__(self, debug=True, str_position=None, colors=None):
        self.cube = Cube(debug=debug, str_position=str_position, colors=colors)
        self.debug = debug
        # database init
        self.engine = create_engine("sqlite:///database.sqlite", echo=False, encoding="utf-8")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        
    def main(self):
        #solu = Solution("R", 1)
        #pos1 = Position("0,-1,1,2,-1,-1,5|1,-1,-1,2,-1,-1,5|2,0,-1,2,-1,-1,5|3,-1,1,2,-1,-1,-1|4,-1,-1,2,-1,-1,-1|5,0,-1,2,-1,-1,-1|6,-1,1,2,-1,4,-1|7,-1,-1,2,-1,4,-1|8,0,-1,2,-1,4,-1|9,-1,1,-1,-1,-1,5|10,-1,-1,-1,-1,-1,5|11,0,-1,-1,-1,-1,5|12,-1,1,-1,-1,-1,-1|13,0,-1,-1,-1,-1,-1|14,-1,1,-1,-1,4,-1|15,-1,-1,-1,-1,4,-1|16,0,-1,-1,-1,4,-1|17,-1,1,-1,3,-1,5|18,-1,-1,-1,3,-1,5|19,0,-1,-1,3,-1,5|20,-1,1,-1,3,-1,-1|21,-1,-1,-1,3,-1,-1|22,0,-1,-1,3,-1,-1|23,-1,1,-1,3,4,-1|24,-1,-1,-1,3,4,-1|25,0,-1,-1,3,4,-1")
        #pos2 = Position("0,-1,1,2,-1,-1,5|1,-1,-1,2,-1,-1,5|8,0,-1,4,-1,-1,2|3,-1,1,2,-1,-1,-1|4,-1,-1,2,-1,-1,-1|16,0,-1,4,-1,-1,-1|6,-1,1,2,-1,4,-1|7,-1,-1,2,-1,4,-1|25,0,-1,4,-1,3,-1|9,-1,1,-1,-1,-1,5|10,-1,-1,-1,-1,-1,5|5,0,-1,-1,-1,-1,2|12,-1,1,-1,-1,-1,-1|13,0,-1,-1,-1,-1,-1|14,-1,1,-1,-1,4,-1|15,-1,-1,-1,-1,4,-1|22,0,-1,-1,-1,3,-1|17,-1,1,-1,3,-1,5|18,-1,-1,-1,3,-1,5|2,0,-1,-1,5,-1,2|20,-1,1,-1,3,-1,-1|21,-1,-1,-1,3,-1,-1|11,0,-1,-1,5,-1,-1|23,-1,1,-1,3,4,-1|24,-1,-1,-1,3,4,-1|19,0,-1,-1,5,3,-1")
        #session.add_all([solu, pos1, pos2])
        #session.commit()
        #ba = BeforeAfter(solu.id, pos1.id, pos2.id)
        #session.add(ba)
        #session.commit()
        if self.debug:
            print "[*] normal"
            self.cube.show_faces(standard=False)
            print "[*] standard"
            self.cube.show_faces(standard=True)
        
        self.first_position = self.cube.get_str_position(standard=True)
        self.searched_processes = {"num_of_moves":0}
        self.goal = "0,-1,1,2,-1,-1,5|1,-1,-1,2,-1,-1,5|2,0,-1,2,-1,-1,5|3,-1,1,2,-1,-1,-1|4,-1,-1,2,-1,-1,-1|5,0,-1,2,-1,-1,-1|6,-1,1,2,-1,4,-1|7,-1,-1,2,-1,4,-1|8,0,-1,2,-1,4,-1|9,-1,1,-1,-1,-1,5|10,-1,-1,-1,-1,-1,5|11,0,-1,-1,-1,-1,5|12,-1,1,-1,-1,-1,-1|13,0,-1,-1,-1,-1,-1|14,-1,1,-1,-1,4,-1|15,-1,-1,-1,-1,4,-1|16,0,-1,-1,-1,4,-1|17,-1,1,-1,3,-1,5|18,-1,-1,-1,3,-1,5|19,0,-1,-1,3,-1,5|20,-1,1,-1,3,-1,-1|21,-1,-1,-1,3,-1,-1|22,0,-1,-1,3,-1,-1|23,-1,1,-1,3,4,-1|24,-1,-1,-1,3,4,-1|25,0,-1,-1,3,4,-1"

        ret = self.loop("", self.first_position)
        if ret:
            print 
            print "[*] Solution Found!!"
            print ">", ret[0]
            print "length:", ret[1]
        else:
            print
            print "[*] couldn't find!!"
        return

    def loop(self, cur_depth, p):
        print cur_depth, p
        session = self.Session()
        query = session.query(BeforeAfter).join(Position, "before_position").filter(Position.position==p)
        if query.count() == 0:
            # to clear up
            del_item_from_dict_by_key_str(self.searched_processes, cur_depth)
            print self.searched_processes
            print "dead branch"
            ret = None
        else:
            for ba in query.all():
                self.searched_processes[str(ba.id)] = {"num_of_moves":
                                                      get_value_from_dict_by_key_str(self.searched_processes, cur_depth+".num_of_moves") + ba.solution.num_of_moves, 
                                                  }
                print self.searched_processes
                if ba.after_position.position == self.goal:
                    print "[*] Found!"
                    move_notations = ""
                    for ba_id in cur_depth.split("."):
                        ba = session.query(BeforeAfter).get(int(ba.id))
                        move_notations += ba.solution.move_notations
                    print "[*] solution:", move_notations
                    print "[*] number of moves:", get_value_from_dict_by_key_str(self.searched_processes, cur_depth+".num_of_moves")
                    ret = (ba.solution.move_notations, ba.solution.num_of_moves)
                else:
                    print "new branch"
                    ret = self.loop(cur_depth+".%d" % ba.id, ba.after_position.position)
                    if ret:
                        ret = (ba.solution.move_notations + ret[0], ret[1] + ba.solution.num_of_moves)
        session.close()
        return ret
        
    def add_data(self, batch, colors):
        # colors: ex.)"URRURRRRR|OOUOOUOOO|WWWWWWUUU|BUBBBBBBB|GGGGGGGGG|YYYYYYYYY"
        # "U" = UNDEFINED
        undefined = []
        unused_colors = [9, 9, 9, 9, 9, 9] # for R,L,U,D,F,B
        faces_colors = [[None, None, None, None, None, None, None, None, None], [None, None, None, None, None, None, None, None, None], [None, None, None, None, None, None, None, None, None], [None, None, None, None, None, None, None, None, None], [None, None, None, None, None, None, None, None, None], [None, None, None, None, None, None, None, None, None]] #[[None]*9]*6
        #faces_colors = self.cube.show_faces(get_only=True, standard=False, color_num=True)
        print faces_colors
        for i1, f in enumerate(colors.split("|")):
            for i2, c in enumerate(f):
                if c == "U":  # UNDEFINED
                    undefined.append((i1, i2))
                elif c in COLOR[:-3]: # DEFINED
                    i = COLOR.index(c)
                    unused_colors[i] -= 1
                    faces_colors[i1][i2] = i
                    print (i1, i2), i, faces_colors
                    raw_input()
                else:
                    print "[*] invalid FACE_VIEWS including 'UNDEFINED'!"
                    raise
        print faces_colors
        print undefined
        print unused_colors
        unused_ncolor = []
        for i, c in enumerate(unused_colors):
            for x in xrange(c):
                unused_ncolor.append(i)

        assert len(unused_ncolor) == len(undefined)

        for perm in itertools.permutations(unused_ncolor):
            for i,p in zip(undefined, perm):
                faces_colors[i[0]][i[1]] = p
            if not self.cube.set_by_faces_color(faces_colors, quiet=True):
                continue
            else:
                #print "ok", faces_colors
                self.update_db(batch)
        return

    def update_db(self, batch):
        session = self.Session()
        # before position
        p = self.cube.get_str_position(standard=True)
        print p
        query = session.query(Position).filter(Position.position==p)
        if query.count() > 0:
            before_pos = query.first()
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

    def check_positions_in_db(self):
        session = self.Session()
        query = session.query(Position)
        for pos in query.all():
            print "[*] <Position(%d)>" % pos.id
            self.cube.set_str_position(pos.position)
            self.cube.show_faces(standard=False) # whichever
            print
        session.close()
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
                      help="check positions in database (for debug/need not specify FACE_VIEWS)")
    (options, args) = parser.parse_args()

    if len(args) > 0:
        if options.add:
            s = Solver(debug=options.debug)
            s.add_data(options.add, colors=args[0])
        elif options.solve:
            s = Solver(colors=args[0], debug=options.debug)
            s.main()
        else:
            parser.print_help()
    else: # there's no FACE_VIEW
        if options.checkp:
            s = Solver()
            s.check_positions_in_db()
        else:
            parser.print_help()
