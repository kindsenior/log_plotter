#!/bin/bash
script_dir=$(cd $(dirname $(readlink -f $0 || echo $0));pwd -P)
gnome-terminal -t "plot" -x $SHELL -ic $script_dir'/../datalogger-plotter-with-pyqtgraph.py -f ${NAUTILUS_SCRIPT_SELECTED_FILE_PATHS%.*} --plot $(zenity --file-selection --filename="'$script_dir'/../config/default.yaml" --file-filter=*.yaml) --layout $(zenity --file-selection --filename="'$script_dir'/../config/default.yaml" --file-filter=*.yaml)|| (echo -e "Fail to execute\nYou have 10s to check the error message." && sleep 10s)'
