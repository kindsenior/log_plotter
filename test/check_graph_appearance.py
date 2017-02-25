#!/usr/bin/python
#-*- coding:utf-8 -*-

import argparse
import signal
import pyqtgraph
from test_util import log_plotter_exec


def show_graph():
    layout =u'''
main:
  graph of dummy:
    legends:
      - { key: dummy, id: [0] }
      - { key: dummy, id: [0] }
'''
    a = log_plotter_exec(layout=layout,
                         plot_conf ='config/sample_plot.yaml',
                         fname = 'data/sample/sample_data')
    a.view.showMaximized()
    return a
        
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='plot data from hrpsys log')
    parser.add_argument("-i", action='store_true', help='interactive (start IPython)')
    parser.set_defaults(feature=False)
    args = parser.parse_args()

    app = pyqtgraph.Qt.QtGui.QApplication([])
    a = show_graph()
    if args.i:
        [app.processEvents() for i in range(2)]
        # start ipython
        print '====='
        print "please use \033[33mapp.processEvents()\033[m to update graph."
        print "you can use \033[33ma\033[m as LogPlotter instance."
        print '====='
        from IPython import embed
        embed()
    else:
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        pyqtgraph.Qt.QtGui.QApplication.instance().exec_()
