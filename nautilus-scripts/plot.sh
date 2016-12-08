#!/bin/bash
script_dir=$(cd $(dirname $(readlink -f $0 || echo $0));pwd -P)
paths=($(python ${script_dir}/get_yaml_path.py))
plot_yaml=${paths[0]}
layout_yaml=${paths[1]}

gnome-terminal -t 'plot' -x $SHELL -ic "datalogger_plotter_with_pyqtgraph.py -f '${NAUTILUS_SCRIPT_SELECTED_FILE_PATHS%.*}' --plot ${plot_yaml} --layout ${layout_yaml} || (echo -e \"Fail to execute\nYou have 10s to check the error message.\" && sleep 10s)"

