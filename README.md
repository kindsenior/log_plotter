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
