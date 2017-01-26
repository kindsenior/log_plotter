# layout.yamlのオプション
## 1. グラフのオプション
```yaml
main:
  imu_gsensor:
    legends:
      - { key: imu_gsensor, id: [0], label: x }
      - { key: imu_gsensor, id: [1], label: y }
      - { key: imu_gsensor, id: [2], label: z }
    newline: False
    downsampling: {ds: 100, auto: False, mode: peak}
    xRange: {min: 98, max: 118, zero: True}
    left_label: "[m/s^2]"
    bottom_label: Time[s]
```
グラフに対するオプションは，グラフのlegendsと同じ階層に．辞書のkeyとvalueのペアで与える．  
上の例のnewline, downsampling, xRange, left_label, bottom_labelが該当する．  
以下，オプションの説明．

### newline
```yaml
# imu_gsensorとimu_gyrometerのグラフを横に並べる
imu_gsensor:
  legends:
    - { key: imu_gsensor, id: [0]}
  newline: False
imu_gyrometer:
  legends:
    - { key: imu_gyrometer, id: [0]}
```
- True: グラフの改行を行う(default)
- False: グラフの改行を抑制する

### downsampling
```yaml
downsampling: {ds: 100, auto: False, mode: peak}
```
```yaml
downsampling: {} # 省略形
```
グラフをダウンサンプリングして描画する．グラフの描画が重いとき，使用すると良い．  
パラメータとして，ds, auto, modeを辞書形式で与えられるが，いずれも省略できるため，最も簡単には空の辞書を渡すだけで良い．  
ダウンサンプリングしない場合は，downsamplingのオプションをコメントアウトするか，```downsampling: None```とする．  
パラメータの詳細は[pyqtgraphのドキュメント](http://www.pyqtgraph.org/documentation/graphicsItems/plotdataitem.html)を参照．

### xRange/yRange
```yaml
xRange: {min: 30, max: 100, zero: True}
yRange: {min: 0, max: 100}
```
グラフのx軸とy軸の範囲を`[min: 最小値, max: 最大値]`の形式の辞書で与える．  
指定しない場合は，オプションをコメントアウトするか，リストの代わりに```None```を与える．  

`zero: True`を指定すると，xRangeで与えた範囲のminをゼロと表示する．  
例の場合，`zero: True`の場合グラフのｘ軸は0~70secと表示され，  
`zero:False`の場合グラフのｘ軸は30~100secと表示される．  
デフォルトでは，`zero: False`である．

### left_label/bottom_label
```yaml
left_label: "[N]"
bottom_label: Time [s]
```
グラフの縦軸(左)と横軸(下)のラベルを指定する．  
指定しない場合は，オプションをコメントアウトするか，```None```を与える．  
ブラケット(`[]`)は，yamlでリストを表すため，必要に応じてクォーテーションでくくる必要がある．

###  height/width
```yaml
height: 50mm # mm
width: 300   # px
```
グラフのサイズを指定する．  
単位を数値の後ろにつけて記述する．現在サポートされている単位は，pxとmmである．

## 2. 凡例のオプション
```yaml
main:
  imu_gsensor:
    legends:
      - { key: imu_gsensor, id: [0], label: x }
      - { key: imu_gsensor, id: [1], label: y }
      - { key: imu_gsensor, id: [2], label: z }
    newline: False
    downsampling: {ds: 100, auto: False, mode: peak}
    xRange: [0:10]
    left_label: "[m/s^2]"
    bottom_label: Time[s]
```
凡例に対するオプションは，グラフのlegendsリストの中の，各凡例に対応する辞書の中で与える．  
上の例のlabelが該当する．  
以下，オプションの説明．

keyとid以外の凡例のオプションは，plot.yamlの設定をオーバーライドする効果がある．  

### label
```
imu_gsensor:
  legends:
    - { key: imu_gsensor, id: [0], label: x }
    - { key: imu_gsensor, id: [1], label: y }
    - { key: imu_gsensor, id: [2], label: z }
```
凡例の名称を変更する．  
上の例では，凡例の名称を順にx,y,zとしている．

### func
plot.yamlで指定している`func`を上書きする．  
一般的には使用しないが，funcの指定が無い凡例について，  
```yaml
  right_foot_force:
    legends:
      - { key: rmfo_off_rfsensor, id: [0-5], func: plot_inverse}
```
のように指定すると，グラフの符号を反転できるなどの使用方法が考えられる．
