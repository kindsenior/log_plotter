# log-plotter
## Sample Usage
```
python datalogger-plotter-with-pyqtgraph.py -f file-name --plot plot.yaml --layout layout.yaml
```
ex)  
when you want to plot watt of each joint, you need to set following two file.

test-layout.yaml
```
- "group": "watt"                                   # title
  "key": ["watt"]                                   # id to lookup test.yaml
  "index": [[0,1,2,3,4,5]]                          # draw watt[0,1,2,3,4,5]
```

test.yaml
```yaml:plot.yaml
"watt":
  "log": ['RobotHardware0_dq','RobotHardware0_tau'] # log file name
  "func": 'plot_watt'                               # function defined in plot.yaml
  "index": [[0,1,2,3,4,5],[0,1,2,3,4,5]]            # which column to use in log file
```

## About config file
### test-layout.yaml
`test-layout.yaml` は一つのグラフに何の凡例を描画するかを記述する。  
例えば、各関節で消費する電力[W]のグラフを作成する際、関節0~5を描画したい場合は、
グラフのタイトルを"watt", 描画する凡例は"watt", indexは`[[0,1,2,3,4,5]]`とする。  
凡例`watt`の計算方法と描画方法は、後述のtest.yamlと、`plot_method.py`の中で定義されているので、
他の凡例を利用したい場合は、まず、`test.yaml`にすでに定義されていなか確認し、定義されていれば、対応する`key`を指定する。  
`index: [0,1,2,3,4,5]`は、６つのグラフとして、横方向に展開される。
<img src="materials/watt_sample_plot.png" height="320px">  
関節0,2,4のみのグラフを作成したい場合は、
`index: [0,2,4]`とする。
<img src="materials/watt_sample_plot2.png" height="320px">  

### test.yaml
#### introduction
`test.yaml` は、各凡例をどのように描画するかを定義する。  
上述の`watt`の場合は、関節トルクと関節速度の積で求められる。  
そのため、計算手順は、ログファイル`RobotHardware0_dq`,`RobotHardware0_tau`を読み込んで、
対応する関節どうしの値を乗じるという手順になる。  
この計算を、２つの配列

- 各成分が関節速度である配列`RobotHardware0_dq`
- 各成分が関節トルクである配列`RobotHardware0_tau`

の成分ごとの積で、

- 各成分が関節消費エネルギーである配列`watt`

を求めると考える。

#### grammer
以下、各記述の説明。

```
"log": ['RobotHardware0_dq','RobotHardware0_tau']
```
必要な２つのログを順序込みで指定している。
```
"func": 'plot_watt'
```
上の２つのログを、`plot_method.py`で定義された、`plot_watt`関数に渡すことを指定している。
```
"index": [[0,1,2,3,4,5],[0,1,2,3,4,5]]
```


は、配列`RobotHardware0_dq`と`RobotHardware0_tau`の成分は、順にログファイルの`[0,1,2,3,4,5]`列目に記述されていることを示す。

#### plot_method.py
``` python
@staticmethod
def normal(plot_item, times, data_dict, args, indices_list, arg_indices, cur_col, key, i):
    # process
```

##### 変数の意味

|variable |args| indices_list| arg_indices| cur_col| key| i|
|:-----   |:---|:----------- |:-----------|:-------|:-- |:-|
|example  |['RobotHardware0_rfsensor'] | [[0]] |[0] |0 |RobotHardware0_rfsensor| 1|

- args: 関数の引数として渡されるlogファイル名
- indices: arg_indicesの中のどの情報を利用するか
- arg_indices: 各ファイルの何列目を使用するか
- cur_col: 現在描画中の列数(行数は不明)
- key: 判例に表示する名前
- i: 一つのグラフの中の何番目の判例を書いているか

つまり、「ログファイルの何列目」を知るには、
```
indices_list[arg_indices[0]][cur_col]
```
を参照する. (todo: わかりやすくする)










## For Daily Experiment
### Tips

##### Left Click

###### Ubuntu earlier than 14.04
save the following commands as ~/.gnome2/nautilus-scripts/hrpsys-plot.sh and ``chmod +x ~/.gnome2/nautilus-scripts/hrpsys-plot.sh`` and then ``nautilus -q``

###### ubuntu14.04 or above
save the following commands as ~/.local/share/nautilus/scripts/hrpsys-plot.sh and ``chmod +x ~/.local/share/nautilus/scripts/hrpsys-plot.sh`` and then ``nautilus -q``

```bash
#!/bin/bash
gnome-terminal -t "aho" -x $SHELL -ic '$HOME/kuroiwa_demos/python/hrpsys-plot/datalogger-plotter-with-pyqtgraph.py -f ${NAUTILUS_SCRIPT_SELECTED_FILE_PATHS%.*} --conf $(zenity --file-selection --filename="$HOME/kuroiwa_demos/python/hrpsys-plot/config/default.yaml" --file-filter=*.yaml)'
exit
```

###### Ubuntu earlier than 14.04
save the following commands as ~/.gnome2/nautilus-scripts/trim.sh and ``chmod +x ~/.gnome2/nautilus-scripts/trim.sh`` and then ``nautilus -q``

###### ubuntu14.04 or above
save the following commands as ~/.local/share/nautilus/scripts/trim.sh and ``chmod +x ~/.local/share/nautilus/scripts/trim.sh`` and then ``nautilus -q``

```bash
#!/bin/bash
gnome-terminal -t "aho" -x $SHELL -ic '$HOME/myrepo/kuroiwa_demos/python/hrpsys-plot/datalogger-trimmer.py -f $NAUTILUS_SCRIPT_SELECTED_FILE_PATHS --min $(zenity --entry --text="minimum time[s]") --max $(zenity --entry --text="maximum time[s]")'
exit
```
