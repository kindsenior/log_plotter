# test 
## テストの走らせ方
### 仮想ディスプレイのインストールと立ち上げ
```bash
sudo apt-get install xvfb
/sbin/start-stop-daemon --start --quiet --pidfile /tmp/custom_xvfb_99.pid --make-pidfile --background --exec /usr/bin/Xvfb -- :99 -screen 0 1400x900x24 -ac +extension GLX +render # copy from pyqtgraph .travis.yaml
export DISPLAY=:99.0
```

### テストの実行
1. 全部をテスト
```bash
python test_all.py
```
2. 個別にテスト
```bash
python test_xxx.py
```

## テストのTips
- unittestのパッケージを使用.  
- pytestは，catkinとの相性が良くない模様．(devel以下の`__init__.py`の読み込みでエラーが出る)  
- テストを作るには，unittest.TestCaseを継承したクラスに，test_xxxという名称のメソッドを定義して作る，  
- テストを走らせるには，`unittest.main()`を実行すると，`test_xxx`メソッドを順に実行してくれる．  
- assertionは，unittest.TestCaseのメソッドである，assertXXXを利用するとテストが失敗したときに見やすく表示される．

```python
import unittest

class TestXXX(unittest.TestCase):
    def test_hogehoge(self):
        # write test here
        x = 1
        self.assertEqual(x,1,'x is {}. not 1'.format(x))

if __name__ == '__main__':
    unittest.main()
```
- `unittest.main`はテストが終わると，そのまま`exit`しようとするが，ガーベジコレクションの順番によって時々Segmentation Faultが発生する．  
以下のようにテスト終了後に`QtGui.QApplication`の消去を明示的に行うとエラーが消えた．
```python
if __name__ == '__main__':
    app = pyqtgraph.Qt.QtGui.QApplication([])
    try:
        unittest.main()
    finally:
        del app
```


