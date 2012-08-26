python-rubiks\_cube\_solver
====

## 概要 ##
このプログラムは

 - cube.py
   - キューブのシミュレーションスクリプト
 - cube_def.py
   - 定数とかもろもろの定義
 - solver.py
   - twophase.jar

からなる。レポジトリ名に__python__とありますが、Javaのライブラリを使うことになったので[__Jython__](http://www.jython.org/)でのみ動きます。
回転記号を使っているので[ここ](http://www.planet-puzzle.com/cubekaiten.html)と[ここ](http://www.planet-puzzle.com/cube-shift.html)を参照してください。

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
   * ランダムにスクランブル（ごちゃまぜに）します。公式ルールに従い、デフォルトで25手分スクランブルします。
 * -b BATCH, --batch=BATCH
   * `BATCH`に回転記号を指定してその通り回します。
 * -c, --confirm
   * このオプションが指定されると、回転するたびにEnterが押されるまで待ちます。
 * -g, --game
   * 対話形式で入力された回転記号通り回します。confirmオプションに関わらず回すたびに状態を確認できます。

scramble -> batch -> game  
の順に処理が進むので、scrambleとgameを指定して遊ぶなんてこともできるかと。  
こっちのスクリプトはpythonでも動きます。

### solver.py ###
**こっちはjythonでないと動きません。**

    > jython solver.py -h
    Usage: ./solver.py [options] FACE_VIEWS
    
    Options:
      -h, --help            show this help message and exit
      -s, --scramble        scramble before solve (ignore FACE_VIEWS)
      -d, --debug           enable debug mode
      -m MODE, --mode=MODE  specify move-notations mode[NORMAL, ROBOT] (default is
                            NORMAL)

 * -s, --scramble
   * ランダムにスクランブルしたものを解きます。`FACE_VIEWS`に何か指定しても無視されます。
 * -m MODE, --mode=MODE
   * MODEに`NORMAL`か`ROBOT`を指定します。デフォルトは`NORMAL`です。`ROBOT`モードについては以下参照。
   
オプション無しで`FACE_VIEWS`にキューブの最初の状態を指定すると自動で解を探します。  
`FACE_VIEWS`には`RRRRRRRRR|OOOOOOOOO|WWWWWWWWW|BBBBBBBBB|GGGGGGGGG|YYYYYYYYY`といった形式で指定する。  
`R`は赤色、`O`はオレンジ色、`W`は白色、`B`は青色、`G`は緑色、`Y`は黄色を表し、  
右、左、上、下、前、後の順に`|`で区切って各面を指定する。  
それぞれの面は、左上、上、右上、左、真ん中、右、左下、下、右下の順に並べる。  
![展開図](https://github.com/pheehs/python-rubiks_cube_solver/raw/master/tenkai-zu.jpg "展開図")  
(注：色の配色は日本国内で販売されているのメガハウス社製のキューブのもの）

`ROBOT`モードとは、ルービックキューブソルバーロボットに解を渡す時のオプションで、  
ロボットが回すことの出来ない  
`"U", "U'", "U2", "D", "D'", "D2", "E", "E'", "E2", "(u)", "(u')"`  
といった回転記号が現れないように解を最適化するモードです。

解の探索には、Herbert Kociemba氏の公開してくださっている_twophase.jar_というJavaのパッケージを利用しています。  
[ここ](http://kociemba.org/cube.htm)の_Download_からダウンロードできます。

## ToDo ##
 - 解の最適化("NOMAL"も"ROBOT"も)
 - solution の最適化
 - グラフィック
