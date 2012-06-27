python-rubiks\_cube\_solver
====

## 概要 ##
このプログラムは

 - cube.py
   - キューブのシミュレーションスクリプト
 - cube_def.py
   - 定数とかもろもろの定義
 - solver.py
   - キューブのデータベース上の最適解探索スクリプト

からなる。
回転記号を使っているので[ここ](http://www.planet-puzzle.com/cubekaiten.html)を参照してください。

### cube.py ###
    > python cube.py -h
    Usage: cube.py [options] arg  
    
    Options:  
      -h, --help            show this help message and exit  
      -d, --debug           show a look while moving  
      -s, --scramble        scramble before moving  
      -b BATCH, --batch=BATCH  
                            run a batch of move notation  
      -c, --confirm         confirm each steps  
      -g, --game            set gaming mode on  

 * -s, --scramble
   * スクランブル（ごちゃまぜに）します。公式ルールに従い、デフォルトで25手分スクランブルします。
 * -b BATCH, --batch=BATCH
   * BATCHに回転記号を指定してその通り回します。
 * -c, --confirm
   * このオプションが指定されると、回転するたびにEnterが押されるまで待ちます。
 * -g, --game
   * 対話形式で入力された回転記号通り回します。confirmオプションに関わらず回すたびに状態を確認できます。

scramble -> batch -> game  
の順に処理が進むので、scrambleとgameを指定して遊ぶなんてこともできるかと。

### solver.py ###
    > python solver.py -h
    Usage: solver.py [options] FACE_VIEWS (CONST_FILTER)
    
    Options:
      -h, --help            show this help message and exit
      -a BATCH, --add=BATCH
                            add data after running a batch of move notations with
                            CONST_FILTER
      -s, --solve           enable solving mode
      -d, --debug           enable debug mode

database.sqliteにどう動かしたらこうなるというデータをためておいて、  
そのデータベースから適切な手順を組み合わせて全面揃える。SQLAlchemy使用。  
`-s`と、`FACE_VIEWS`にキューブの最初の状態を指定すると自動で解を探す。  
`FACE_VIEWS`には`RRRRRRRRR|OOOOOOOOO|WWWWWWWWW|BBBBBBBBB|GGGGGGGGG|YYYYYYYYY`といった形式で指定する。  
`R`は赤色、`O`はオレンジ色、`W`は白色、`B`は青色、`G`は緑色、`Y`は黄色を表し、  
右、左、上、下、前、後の順に`|`で区切って各面を指定する。  
それぞれの面は、左上、上、右上、左、真ん中、右、左下、下、右下の順に並べる。  
![展開図](https://github.com/pheehs/python-rubiks_cube_solver/raw/master/tenkai-zu.jpg "展開図")

データベスに新規登録もこのスクリプトでやる。  
その場合、`FACE_VIEWS`に動かす前の状態、`CONST_FILTER`を指定して、何色でもいいところを指定する。
決まっている色は`D`、何色でもいいところは`U`を指定する。
すなわち、何色でもいいところにも`FACE_VIEWS`で色を指定する必要があるが、適当な色を入れておく。
`-a BATCH`の`BATCH`には登録する手順を指定。

### database.sqlite ###
```python
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
```
## ToDo ##
 - 回転体
 - 自動で解を見つけ、解く。
   - ループの可能性
   - データベース更新補助のために、UNDEFINEDで指定したところを埋めてくれる関数か何か
 - グラフィック
