python-rubiks\_cube\_solver
====

## 概要 ##
このプログラムは

 - cube.py
   - キューブのシミュレーションスクリプト
 - cube_def.py
   - 定数とかもろもろの定義
 - solver.py
   - `twophase.jar`と`optiqtm`で解を探す。
 - cube_capture.py
   - カメラからキューブの色認識
 - robot_commu.py
   - ロボットとソフトウェアをつなぐ。ロボットとはシリアル通信。

からなる。`solver.py`以外はPythonで動きますが、Javaのライブラリを使う`solver.py`と`solver.py`を呼び出す`robot_commu.py`には[__Jython__](http://www.jython.org/)が必要です。
回転記号を使っているので[ここ](http://www.planet-puzzle.com/cubekaiten.html)と[ここ](http://www.planet-puzzle.com/cube-shift.html)を参照してください。  
全体のつながりを図に表すと以下のようになります。  
![関係図](https://github.com/pheehs/python-rubiks_cube_solver/raw/twophase/relationship.png "関係図")  

### cube.py ###

    $ python cube.py -h
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
![展開図](https://github.com/pheehs/python-rubiks_cube_solver/raw/twophase/tenkai-zu.jpg "展開図")  
(注：色の配色は日本国内で販売されているのメガハウス社製のキューブのもの）

`ROBOT`モードとは、ルービックキューブソルバーロボットに解を渡す時のオプションで、  
ロボットが回すことの出来ない  
`"U", "U'", "U2", "D", "D'", "D2", "E", "E'", "E2", "(u)", "(u')"`  
といった回転記号が現れないように解を最適化するモードです。

解の探索には、`twophase.jar`というJavaのパッケージ、解の最適化には`optiqtm`という実行ファイルをそのまま呼び出しています。  
どちらもHerbert Kociemba氏が[ここ](http://kociemba.org/cube.htm)の`Download`で公開してくださっています。

### cube_capture.py ###
OpenCVがJythonでは動かないので**Python**で動かします。

    $ python cube_capture.py --help
    Usage: ./cube_capture.py [options]
    
    Options:
      -h, --help  show this help message and exit

今のところ特にオプション無し。  
RGB方式の代わりにHSV方式を使ってキューブのステッカーの色を認識します。  
HSV方式・・・ 色相(Hue)/彩度(Saturation)/明度(Value)  
 * 色相　・・・　色の種類を表す。
   * 似た色を隣合うように並べると円環状になるので、基準の色相からの角度で表せる。
 * 彩度　・・・　色の鮮やかさを表す。
   * 鮮やかな色ほど高く、白や灰、黒は低い
 * 明度　・・・　色の明るさを表す。
   * 黒は明度が最小、明るくなり白に近づくほど大きくなる

「赤」と「黒っぽく濁った赤」「白っぽく濁った赤」を見比べてわかるんですが、同じ赤であれば色相は近くなります。この色相の性質を利用することで、多少の光のあたり具合の変化があっても色を認識できるようになります。  

と、ここで気づいた方もいるかも知れませんが、「黒」「灰」「白」の色相は「0~1」となっています。これはどんな値も取りうるという意味で、彩度の低いあるいは明度が極端に小さい場合は色相はほぼ関係なくなります。すると、色相だけを見て色を判断したのでは白色が何色になるかわかりません。
そこで、彩度がある程度低く、明度がある程度高い場合は色相で色を判断する前に「白」であると認識させます。

### robot_commu.py ###
コイツ自体は**Python**で動きますが、`solver.py`を呼び出すので**Jython**が必要です。

    $ python robot_commu.py
    Usage: ./robot_commu.py [options] [DEVICE_NAME]
    
    Options:
      -h, --help            show this help message and exit
      -e, --enum_device     enumerate and select device name (ignore DEVICE_NAME)
      -d, --debug           enable debug mode(withoout robot)
      -o FILEPATH, --dump_file=FILEPATH
                            specify dump file of serial simulation for
                            debug(default is "serial.log")

`DEVICE_NAME`にロボットに搭載したマイコンのシリアル通信用デバイスファイルorCOMポート名を指定してください。

 * -e, --enum_device
   * `/dev/tty.*`を検索して選べるので、`DEVICE_NAME`を指定する必要はありません。
 * -d, --debug
   * マイコンとつながないでテストする用です。デフォルトで`serial.log`に送信するコマンドをダンプします。
 * -o FILEPATH, --dump_file=FILEPATH
   * デバッグ時にダンプするファイルを変更できます。
   
1. まず`cube_capture.py`でキューブの色を認識し、
2. それを`solver.py`に渡し、
3. その結果をマイコンに送って解かせる。

だいたいこんな感じで処理が進みます。

## ToDo ##
 - cube_capture.pyの精度向上
 - グラフィック
