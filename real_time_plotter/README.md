# dataport_publisher
rtcのデータポートの出力をrosのtopicで出します。
OpenRTMのデータポートの型と、ROSのトピックの対応をyamlファイルで与えます。

```
# topicの出力
./dataport_publisher.py config/st_originActCog.yaml

# rqt_plotの軌道
rqt_plot /st_originActCog


