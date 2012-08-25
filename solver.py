#! /usr/bin/env python
#-*- coding: utf-8 -*-

from cube import *
from cube_def import *
from sqlalchemy import create_engine, Column, ForeignKey
from sqlalchemy import Integer, String
from sqlalchemy.orm import relation, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()
import itertools
import datetime

#IS_LIMITED
NORMAL = 0 # without restriction of notations
ROBOT = 1 # cannot run ("U", "U'", "U2", "D", "D'", "D2", "E", "E'", "E2", "(u)", "(u')")
## U = (r)B(r')
## D = (r)F(r')

class Solution(Base):
    __tablename__ = "solutions"
    # some Solution(varied IS_LIMITED) related to one PieceMove
    id = Column(Integer, primary_key=True)
    move_notations = Column(String(100), nullable=False, unique=True) # is 100 enough ?
    num_of_moves = Column(Integer, nullable=False)
    is_limited = Column(Integer, default=NORMAL) # NORMAL or ROBOT
    piece_move_id = Column(Integer, ForeignKey("piece_move.id"))
    piece_move = relation("PieceMove")

    def __init__(self, move_notations, num_of_moves, is_limited, piece_move_id):
        self.move_notations = move_notations
        self.num_of_moves = num_of_moves
        self.is_limited = is_limited
        self.piece_move_id = piece_move_id
        
    def __repr__(self):
        if not self.piece_move_id:
            self.piece_move_id = 0
        return "<Solution(%s, piece_move=%d)>" % (self.move_notations, self.piece_move_id)

class PieceMove(Base):
    __tablename__ = "piece_move"
    # for move only 1 piece to specified location
    id = Column(Integer, primary_key=True)
    before_location = Column(Integer, nullable=False)
    after_location = Column(Integer, nullable=False) # which piece mustn't move is depending on after_location
    center_colors = Column(Integer, nullable=False)
    
    def __init__(self, before_location, after_location, center_colors):
        self.before_location = before_location
        self.after_location = after_location
        self.center_colors = center_colors # slice of ROTATED_CENTER_COLORS

    def __repr__(self):
        assert type(self.before_location) == int
        assert type(self.after_location) == int
        assert type(self.center_colors) == int
        return "<PieceMove(before_loc=%d, after_loc=%d, center_col=%d)>" % (self.before_location, self.after_location, self.center_colors)

class Solver(object):
    def __init__(self, debug=True, str_position=None, colors=None, is_limited=NORMAL):
        self.cube = Cube(debug=debug, str_position=str_position, colors=colors)
        self.debug = debug
        self.is_limited = is_limited
        #self.goal = "0,-1,1,2,-1,-1,5|1,-1,-1,2,-1,-1,5|2,0,-1,2,-1,-1,5|3,-1,1,2,-1,-1,-1|4,-1,-1,2,-1,-1,-1|5,0,-1,2,-1,-1,-1|6,-1,1,2,-1,4,-1|7,-1,-1,2,-1,4,-1|8,0,-1,2,-1,4,-1|9,-1,1,-1,-1,-1,5|10,-1,-1,-1,-1,-1,5|11,0,-1,-1,-1,-1,5|12,-1,1,-1,-1,-1,-1|13,0,-1,-1,-1,-1,-1|14,-1,1,-1,-1,4,-1|15,-1,-1,-1,-1,4,-1|16,0,-1,-1,-1,4,-1|17,-1,1,-1,3,-1,5|18,-1,-1,-1,3,-1,5|19,0,-1,-1,3,-1,5|20,-1,1,-1,3,-1,-1|21,-1,-1,-1,3,-1,-1|22,0,-1,-1,3,-1,-1|23,-1,1,-1,3,4,-1|24,-1,-1,-1,3,4,-1|25,0,-1,-1,3,4,-1"
        # database init
        self.engine = create_engine("sqlite:///database.sqlite", encoding="utf-8")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        # solution
        self.solution = ""
        self.num_of_moves = 0


    def lbl_run(self):
        start_time = datetime.datetime.now()
        ret = self.lbl_stage1()
        if not ret:
            return
        delta = datetime.datetime.now() - start_time
        print "Running time: %ddays %dh:%dm:%d.%ds" % (delta.days, delta.seconds / 3600, (delta.seconds % 3600) / 60, (delta.seconds % 3600) % 60, delta.microseconds)
        print 

        return

    def lbl_stage1(self):
        session = self.Session()                
        self.cube.show_faces()
        print "<stage 1>  Cross on [Down]"
        for piece_num, after_loc in [(18, L_DB), (20, L_DL), (22, L_DR), (24, L_DF)]: # BY, BO, BR, BG
            before_loc,piece = self.cube.get_piece_location(piece_num)
            center_colors = piece.get_center_colors()
            if (before_loc == after_loc) and (center_colors == 0):
                if self.debug: 
                    print "[*] Already at the position. (nop)"
                continue
            q = session.query(PieceMove)\
                .filter(PieceMove.before_location == before_loc)\
                .filter(PieceMove.after_location == after_loc)\
                .filter(PieceMove.center_colors == center_colors)
            if q.count() < 1:
                print "[*] Database is not completed. Please add following pattern:"
                print "<PieceMove(before_loc=%d, after_loc=%d, center_col=%d)>" % (before_loc, after_loc, center_colors)
                session.close()
                return False
            else: # PieceMove found
                pm = q.first()
                solu_q = session.query(Solution).filter(Solution.piece_move==pm).filter(Solution.is_limited==self.is_limited)
                if solu_q.count() < 1:
                    print "[*] Database is not completed. Please add following pattern:"
                    print "<Solution(piece_move=%d, is_limited=%d)>" % (pm.id, self.is_limited)
                    session.close()
                    return False
                else: # Solution found
                    solu = solu_q.first()
                    self.solution += solu.move_notations
                    self.cube.run(solu.move_notations, confirm=False, quiet=True)
                    self.num_of_moves += solu.num_of_moves
                    if self.debug:
                        print "[*] please rotate like this(%d moves):" % solu.num_of_moves, solu.move_notations
                        raw_input("continue?>")
                        print "<Current Situation>",
                        self.cube.show_faces()
                        raw_input("continue?>")
                    continue
        self.cube.show_faces()
        session.close()
        return True
    
    def db_edit_for_lbl1(self):
        # when after_location=18 , this func will auto fill 20, 22, 24
        session = self.Session()

        self.cube.__init__(debug=False)
        prev_center_colors = (None, None)
        for i,pnl in enumerate([(22, L_DR), (24, L_DF), (20, L_DL)]):
            piece_num, after_loc = pnl

            self.cube.run("(u)")
            #backup_pos = self.cube.get_str_position()
            for pm in session.query(PieceMove).filter(PieceMove.after_location==18).all():
                solu_q = session.query(Solution).filter(Solution.piece_move==pm).filter(Solution.is_limited==ROBOT)
                if solu_q.count() < 1:
                    return False
                else:
                    solu = solu_q.first()

                    before_location=self.cube.get_piece_location(pm.before_location)[0]
                    translated_notations = self.cube.translate_batch(solu.move_notations)
                    #self.cube.init()
                    #self.cube.run(translated_notations, quiet=True)
                    #center_colors = ROTATED_CENTER_COLORS.index(tuple([range(6).index(c) for c in ROTATED_CENTER_COLORS[self.cube.get_piece_location(piece_num)[1].get_center_colors()]]))
                    #self.cube.set_str_position(backup_pos)
                    new_pm = PieceMove(before_location=before_location, after_location=after_loc, center_colors=0) ## have to edit center_colors by hand
                    session.add(new_pm)
                    session.commit() ## cannot get new_pm.id before commit new_pm
                    
                    new_solu =  Solution(move_notations=translated_notations,
                                         num_of_moves=solu.num_of_moves, is_limited=solu.is_limited, piece_move_id=new_pm.id)
                    session.add(new_solu)
                    session.commit()
                    
                    print new_pm, new_solu
                    
                    if prev_center_colors[0] == before_location:
                        new_pm.center_colors = 
                    new_pm.center_colors = int(raw_input("center_colors>"))
                    prev_center_colors = (before_location, new_pm.center_colors) # cache
                    session.add(new_pm)
                    session.commit()
                    # before n  -> ???
                    # after  18 -> 20, 22, 24
            
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
    parser.add_option("", "--db_edit", dest="stage",
                      default=None, help="<for dev>database edit for STAGE(ex.'lbl1', 'lbl2'")
    (options, args) = parser.parse_args()

    if len(args) > 0:
        if options.solve:
            s = Solver(colors=args[0], debug=options.debug)
            s.lbl_run()
        else:
            parser.print_help()
    else: # there's no FACE_VIEW
        if options.stage:
            s = Solver()
            func = getattr(s, "db_edit_for_"+options.stage, lambda :"Error:\n[*]invalid STAGE!")
            print func()
        else:
            parser.print_help()
include/asm-generic/bitops/ext2-atomic-setbit.h\
include/asm-generic/bitops/ext2-atomic.h\
include/asm-generic/bitops/ffs.h\
include/asm-generic/bitops/ffz.h\
include/asm-generic/bitops/find.h\
include/asm-generic/bitops/fls.h\
include/asm-generic/bitops/fls64.h\
include/asm-generic/bitops/hweight.h\
include/asm-generic/bitops/le.h\
include/asm-generic/bitops/lock.h\
include/asm-generic/bitops/non-atomic.h\
include/asm-generic/bitops/sched.h\
include/asm-generic/bitops.h\
include/asm-generic/bitsperlong.h\
include/asm-generic/bug.h\
include/asm-generic/bugs.h\
include/asm-generic/cache.h\
include/asm-generic/cacheflush.h\
include/asm-generic/checksum.h\
include/asm-generic/cmpxchg-local.h\
include/asm-generic/cmpxchg.h\
include/asm-generic/cputime.h\
include/asm-generic/current.h\
include/asm-generic/delay.h\
include/asm-generic/device.h\
include/asm-generic/div64.h\
include/asm-generic/dma-coherent.h\
include/asm-generic/dma-mapping-broken.h\
include/asm-generic/dma-mapping-common.h\
include/asm-generic/dma.h\
include/asm-generic/emergency-restart.h\
include/asm-generic/errno-base.h\
include/asm-generic/errno.h\
include/asm-generic/exec.h\
include/asm-generic/fb.h\
include/asm-generic/fcntl.h\
include/asm-generic/ftrace.h\
include/asm-generic/futex.h\
include/asm-generic/getorder.h\
include/asm-generic/gpio.h\
include/asm-generic/hardirq.h\
include/asm-generic/hw_irq.h\
include/asm-generic/ide_iops.h\
include/asm-generic/int-l64.h\
include/asm-generic/int-ll64.h\
include/asm-generic/io-64-nonatomic-hi-lo.h\
include/asm-generic/io-64-nonatomic-lo-hi.h\
include/asm-generic/io.h\
include/asm-generic/ioctl.h\
include/asm-generic/ioctls.h\
include/asm-generic/iomap.h\
include/asm-generic/ipcbuf.h\
include/asm-generic/irq.h\
include/asm-generic/irq_regs.h\
include/asm-generic/irqflags.h\
include/asm-generic/Kbuild\
include/asm-generic/Kbuild.asm\
include/asm-generic/kdebug.h\
include/asm-generic/kmap_types.h\
include/asm-generic/libata-portmap.h\
include/asm-generic/linkage.h\
include/asm-generic/local.h\
include/asm-generic/local64.h\
include/asm-generic/memory_model.h\
include/asm-generic/mm_hooks.h\
include/asm-generic/mman-common.h\
include/asm-generic/mman.h\
include/asm-generic/mmu.h\
include/asm-generic/mmu_context.h\
include/asm-generic/module.h\
include/asm-generic/msgbuf.h\
include/asm-generic/mutex-dec.h\
include/asm-generic/mutex-null.h\
include/asm-generic/mutex-xchg.h\
include/asm-generic/mutex.h\
include/asm-generic/page.h\

include/asm-generic/param.h\
include/asm-generic/parport.h\
include/asm-generic/pci-bridge.h\
include/asm-generic/pci-dma-compat.h\
include/asm-generic/pci.h\
include/asm-generic/pci_iomap.h\
include/asm-generic/percpu.h\
include/asm-generic/pgalloc.h\
include/asm-generic/pgtable-nopmd.h\
include/asm-generic/pgtable-nopud.h\
include/asm-generic/pgtable.h\
include/asm-generic/poll.h\
include/asm-generic/posix_types.h\
include/asm-generic/ptrace.h\
include/asm-generic/resource.h\
include/asm-generic/rtc.h\
include/asm-generic/rwsem.h\
include/asm-generic/scatterlist.h\
include/asm-generic/sections.h\
include/asm-generic/segment.h\
include/asm-generic/sembuf.h\
include/asm-generic/serial.h\
include/asm-generic/setup.h\
include/asm-generic/shmbuf.h\
include/asm-generic/shmparam.h\
include/asm-generic/siginfo.h\
include/asm-generic/signal-defs.h\
include/asm-generic/signal.h\
include/asm-generic/sizes.h\
include/asm-generic/socket.h\
include/asm-generic/sockios.h\
include/asm-generic/spinlock.h\
include/asm-generic/stat.h\
include/asm-generic/statfs.h\
include/asm-generic/string.h\
include/asm-generic/swab.h\
include/asm-generic/switch_to.h\
include/asm-generic/syscall.h\
include/asm-generic/syscalls.h\
include/asm-generic/termbits.h\
include/asm-generic/termios-base.h\
include/asm-generic/termios.h\
include/asm-generic/timex.h\
include/asm-generic/tlb.h\
include/asm-generic/tlbflush.h\
include/asm-generic/topology.h\
include/asm-generic/types.h\
include/asm-generic/uaccess-unaligned.h\
include/asm-generic/uaccess.h\
include/asm-generic/ucontext.h\
include/asm-generic/unaligned.h\
include/asm-generic/unistd.h\
include/asm-generic/user.h\
include/asm-generic/vga.h\
include/asm-generic/vmlinux.lds.h\
include/asm-generic/xor.h\
