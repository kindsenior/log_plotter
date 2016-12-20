#!/bin/bash
script_dir=$(cd $(dirname $(readlink -f $0 || echo $0));pwd -P)
# use zenity
# gnome-terminal -t "plot" -x $SHELL -ic 'datalogger_plotter_with_pyqtgraph.py -f ${NAUTILUS_SCRIPT_SELECTED_FILE_PATHS%.*} --plot $(zenity --file-selection --filename="'$script_dir'/../config/default.yaml" --file-filter=*_plot.yaml) --layout $(zenity --file-selection --filename="'$script_dir'/../config/default.yaml" --file-filter=*_layout.yaml)|| (echo -e "Fail to execute\nYou have 10s to check the error message." && sleep 10s)'
# use qt gui
gnome-terminal -t "plot" -x $SHELL -ic 'datalogger_plotter_with_pyqtgraph.py -f ${NAUTILUS_SCRIPT_SELECTED_FILE_PATHS%.*} || (echo -e "Fail to execute\nYou have 10s to check the error message." && sleep 10s)'
