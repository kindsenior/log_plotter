#!/usr/bin/env python

import argparse
import csv
import functools
import math
import multiprocessing
import numpy
import struct
import sys
import time
import yaml
import plot_method
import re
import copy
from graph_tree import *

try:
    import pyqtgraph
except:
    print "please install pyqtgraph. see http://www.pyqtgraph.org/"
    sys.exit(1)


# decorator for time measurement
def my_time(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        print("start : " + func.func_name)
        result = func(*args, **kwargs)
        print('{0:>10} : {1:3.3f} [s]'.format(func.func_name,
                                              time.time() - start))
        return result
    return wrapper


# seems that we should declare global function for multiprocess
def readOneTopic(fname):
    tmp = []
    with open(fname, 'r') as f:
        reader = csv.reader(f, delimiter=' ')
        for row in reader:
            dl = filter(lambda x: x != '', row)
            tmp.append([float(x) for x in dl])
    return numpy.array(tmp)

class DataloggerLogParser:
    def __init__(self, fname, plot_conf_name, layout_conf_name, title):
        self.fname = fname
        with open(plot_conf_name, "r") as f:
            self.plot_dict = yaml.load(f)
        with open(layout_conf_name, "r") as f:
            self.layout_list = yaml.load(f)
        # setup view
        self.view = pyqtgraph.GraphicsLayoutWidget()
        self.view.setBackground('w')
        self.view.setWindowTitle(title if title else fname.split('/')[-1])
        # self.dateListDict is set by self.readData()
        self.dataListDict = {}# todo: to list of dictionary
        # back up for plot items
        self.plotItemOrig = {}

    def _arange_yaml_before_readData (self):
        '''
        fix yaml format
        from
        ```yaml
        - 'group': "joint_angle"
          'key': ['sh_qOut', 'abc_q', 'st_q', 'RobotHardware0_q']
          'index': [["0:6"],["0:6"],["0:6"],["0:6"]]
        - 'index': [["6:12"],["6:12"],["6:12"],["6:12"]]

        ```
        to
        ```yaml
        - 'group': "joint_angle"
          'key': ['sh_qOut', 'abc_q', 'st_q', 'RobotHardware0_q']
          'index': [["0:6"],["0:6"],["0:6"],["0:6"]]
        - 'group': "joint_angle"
          'key': ['sh_qOut', 'abc_q', 'st_q', 'RobotHardware0_q']
          'index': [["6:12"],["6:12"],["6:12"],["6:12"]]
        ```
        '''
        # complete 'group' and 'key' in layout_list
        assert (self.layout_list[0].has_key('group'))
        assert (self.layout_list[0].has_key('key'))
        # layout yaml
        for i, row_layout in enumerate(self.layout_list):
            if not row_layout.has_key('group'):
                row_layout['group'] = self.layout_list[i-1]['group']
            if not row_layout.has_key('key'):
                row_layout['key'] = self.layout_list[i-1]['key']
            if not row_layout.has_key('name'):
                row_layout['name'] = copy.copy(row_layout['key'])
        # plot.yaml
        for rule_tupple in self.plot_dict.items():
            if not rule_tupple[1].has_key('func'):
                rule_tupple[1]['func'] = 'normal'

    def _arange_yaml_after_readData (self):
        '''
        from:
            'index': [["0:6"],["0:6"],["0:6"],["0:6"]]
        to:
            'index': [[0,1,2,3,4,5],[0,1,2,3,4,5],[0,1,2,3,4,5],[0,1,2,3,4,5]]
        '''
        used_keys = list(set(reduce(lambda x,y: x+y, [group["key"] for group in self.layout_list])))
        for key in self.plot_dict.keys():
            if not key in used_keys:
                continue
            index_field = self.plot_dict[key]['index'] # ex. [['0:6'], ['0:6']]
            for i,_ in enumerate(index_field):
                if type(index_field[i][0]) == str:
                    parsed_index = re.match("([0-9]+):([0-9]+)", index_field[i][0])
                    if parsed_index:
                        index_field[i] = range(int(parsed_index.group(1)),int(parsed_index.group(2)))
                        continue
                    parsed_index = re.match("([0-9]+):", index_field[i][0])
                    if parsed_index:
                        log_name = self.plot_dict[key]['log'][i]
                        data_row_length = len(self.dataListDict[log_name][0]) -1
                        index_field[i] = range(int(parsed_index.group(1)), data_row_length)
                        continue
        # parse layout_list
        for row_layout in self.layout_list:
            index_field = row_layout['index'] # ex. [['0:6'], ['0:6'], ['0:6'], ['0:6']]
            key = row_layout['key']
            for i,_ in enumerate(index_field):
                if type(index_field[i][0]) == str:
                    parsed_index = re.match("([0-9]+):([0-9]+)", index_field[i][0])
                    if parsed_index:
                        index_field[i] = range(int(parsed_index.group(1)),int(parsed_index.group(2)))
                        continue
                    parsed_index = re.match("([0-9]+):", index_field[i][0])
                    if parsed_index:
                        max_len = len(self.plot_dict[key[i]]['index'][0])
                        index_field[i] = range(int(parsed_index.group(1)), max_len)
                        continue

    @my_time
    def readData(self):
        '''
        read log data from log files and store dataListDict
        # self.dataListDict[topic] = numpy.array([[t_0, x_0, y_0, ...],
        #                                         [t_1, x_1, y_1, ...],
        #                                         ...,
        #                                         [t_n, x_n, y_n, ...]])
        '''
        # fix yaml
        self._arange_yaml_before_readData()
        used_keys = list(set(reduce(lambda x,y: x+y, [group["key"] for group in self.layout_list])))
        topic_list = list(set(reduce(lambda x,y: x+y, [self.plot_dict[used_key]["log"] for used_key in used_keys] )))
        # store data in parallel
        fname_list = [self.fname+'.'+ext for ext in topic_list]
        pl = multiprocessing.Pool()
        data_list = pl.map(readOneTopic, fname_list)
        for topic, data in zip(topic_list, data_list):
            self.dataListDict[topic] = data
        # set the fastest time as 0
        min_time = min([self.dataListDict[topic][0][0] for topic in topic_list])
        for topic in topic_list:
            raw_time = self.dataListDict[topic][:, 0]
            self.dataListDict[topic][:, 0] = [x - min_time for x in raw_time]
        # fix servoState
        if 'RobotHardware0_servoState' in topic_list:
            def servoStatesConverter(x):
                return struct.unpack('f', struct.pack('i', int(x)))[0]
            vf = numpy.vectorize(servoStatesConverter)
            ss_tmp = self.dataListDict['RobotHardware0_servoState'][:, 1:]
            self.dataListDict['RobotHardware0_servoState'][:, 1:] = vf(ss_tmp)
        # fix yaml
        self._arange_yaml_after_readData()

    @my_time
    def setLayout(self):
        '''
        set layout of view according to self.plot_dict
        '''
        self.graph_tree = GraphGroupTree(self.layout_list, self.plot_dict)
        # set graphItem
        for col_num in RowColInterface.layout:
            for j in range(col_num):
                self.view.addPlot()
            self.view.nextRow()
        # set grid
        for plot_item in a.view.ci.items.keys():
            plot_item.showGrid(x=True, y=True)
            # we should call addLegend once a plot item
            plot_item.addLegend(offset=(0, 0))
        # set tile
        for graph_group in self.graph_tree:
            for graph in graph_group:
                row = graph.row()
                col = graph.col()
                title = graph.name
                plot_item = a.view.ci.rows[row][col]
                plot_item.setTitle(title)

    @my_time
    def plotData(self):
        '''
        plot
        '''
        times = self.dataListDict.items()[0][1][:,0]
        # geneerate data_dict
        used_keys = list(set(reduce(lambda x,y: x+y, [group["key"] for group in self.layout_list])))
        topic_list = list(set(reduce(lambda x,y: x+y, [self.plot_dict[used_key]["log"] for used_key in used_keys] )))
        data_dict = {}
        for log in topic_list:
            data_dict[log] = self.dataListDict[log][:, 1:]

        for graph_group in self.graph_tree:
            for graph in graph_group:
                for legend in graph:
                    row = graph.row()
                    col = graph.col()
                    plot_item = a.view.ci.rows[row][col] # canvas to draw
                    func = legend.how_to_plot['func']    # function in plot_method (ex. 'plot_watt')
                    logs = legend.how_to_plot['log']     # list of log (ex. ['RobotHardware0_dq', 'RobotHardware0_tau'])
                    log_cols = legend.how_to_plot['index']   # columns in log (ex. [0, 0])
                    i = legend.index                     # if there are three legend in one graph, i = 0 or 1 or 2.
                    key = legend.layout['name']
                    getattr(plot_method.PlotMethod, func) (plot_item, times, data_dict, logs, log_cols, col, key, i)

    @my_time
    def setLabel(self):
        '''
        set label: time for bottom plots, unit for left plots
        '''
        row_num = len(self.view.ci.rows)
        # left plot items
        for i in range(row_num):
            cur_item = self.view.ci.rows[i][0]
            title = cur_item.titleLabel.text
            tmp_units = None
            if ("12V" in title) or ("80V" in title):
                tmp_units = "V"
            elif "current" in title:
                tmp_units = "A"
            elif ("temperature" in title) or ("joint_angle" in title) or ("attitude" in title) or ("tracking" in title):
                tmp_units = "deg"
            elif ("joint_velocity" in title):
                tmp_units = "deg/s"
            elif ("watt" in title):
                tmp_units = "W"
            cur_item.setLabel("left", text="", units=tmp_units)
            # we need this to suppress si-prefix until https://github.com/pyqtgraph/pyqtgraph/pull/293 is merged
            for ax in cur_item.axes.values():
                ax['item'].enableAutoSIPrefix(enable=False)
                ax['item'].autoSIPrefixScale = 1.0
                ax['item'].labelUnitPrefix = ''
                ax['item'].setLabel()
        # bottom plot items
        col_num = len(self.view.ci.rows[row_num-1])
        for i in range(col_num):
            cur_item = self.view.ci.rows[row_num-1][i]
            cur_item.setLabel("bottom", text="time", units="s")

    @my_time
    def linkAxes(self):
        '''
        link all X axes and some Y axes
        '''
        # X axis
        all_items = self.view.ci.items.keys()
        target_item = all_items[0]
        for i, p in enumerate(all_items):
            if i != 0:
                p.setXLink(target_item)
            else:
                p.enableAutoRange()
        # Y axis
        for cur_row_dict in self.view.ci.rows.values():
            all_items = cur_row_dict.values()
            target_item = all_items[0]
            title = target_item.titleLabel.text
            if title.find("joint_angle") == -1 and title.find("_force") == -1 and title != "imu" and title.find("comp") == -1:
                y_min = min([ci.viewRange()[1][0] for ci in all_items])
                y_max = max([ci.viewRange()[1][1] for ci in all_items])
                target_item.setYRange(y_min, y_max)
                for i, p in enumerate(all_items):
                    if i != 0:
                        p.setYLink(target_item)

    @my_time
    def customMenu(self):
        '''
        customize right-click context menu
        '''
        self.plotItemOrig = self.view.ci.items.copy()
        all_items = self.view.ci.items.keys()
        for pi in all_items:
            vb = pi.getViewBox()
            hm = vb.menu.addMenu('Hide')
            qa1 = hm.addAction('hide this plot')
            qa2 = hm.addAction('hide this row')
            qa3 = hm.addAction('hide this column')
            qa4 = vb.menu.addAction('restore plots')
            qa5 = hm.addAction('hide except this plot')
            qa6 = hm.addAction('hide except this row')
            qa7 = hm.addAction('hide except this colmn')
            def hideCB(item):
                self.view.ci.removeItem(item)
            def hideRowCB(item):
                r, _c = self.view.ci.items[item][0]
                del_list = [self.view.ci.rows[r][c] for c in self.view.ci.rows[r].keys()]
                for i in del_list:
                    self.view.ci.removeItem(i)
            def hideColCB(item):
                _r, c = self.view.ci.items[item][0]
                del_list = []
                row_num = len(self.view.ci.rows)
                for r in range(row_num):
                    if c in self.view.ci.rows[r].keys():
                        del_list.append(self.view.ci.rows[r][c])
                for i in del_list:
                    self.view.ci.removeItem(i)
            def hideExcCB(item):
                del_list = self.view.ci.items.keys()
                del_list.remove(item)
                for i in del_list:
                    self.view.ci.removeItem(i)
            def hideExcRowCB(item):
                del_list = self.view.ci.items.keys()
                r, _c = self.view.ci.items[item][0]
                not_del_list=[self.view.ci.rows[r][c] for c in self.view.ci.rows[r].keys()]
                for i in del_list:
                    if i in not_del_list:
                        del_list.remove(i)
                for i in del_list:
                    self.view.ci.removeItem(i)
            def hideExcColumnCB(item):
                del_list = self.view.ci.items.keys()
                _r, c = self.view.ci.items[item][0]
                not_del_list=[self.view.ci.rows[r][c] for r in range(len(a.view.ci.rows))]
                for i in del_list:
                    if i in not_del_list:
                        del_list.remove(i)
                for i in del_list:
                    self.view.ci.removeItem(i)
            def restoreCB():
                self.view.ci.clear()
                for key in self.plotItemOrig:
                    r, c = self.plotItemOrig[key][0]
                    self.view.ci.addItem(key, row=r, col=c)
            qa1.triggered.connect(functools.partial(hideCB, pi))
            qa2.triggered.connect(functools.partial(hideRowCB, pi))
            qa3.triggered.connect(functools.partial(hideColCB, pi))
            qa4.triggered.connect(restoreCB)
            qa5.triggered.connect(functools.partial(hideExcCB, pi))
            qa6.triggered.connect(functools.partial(hideExcRowCB, pi))
            qa7.triggered.connect(functools.partial(hideExcColumnCB, pi))

    def main(self):
        '''
        1. read log files
        2. decide layout
        3. plot data
        4. set label
        5. link axes
        6. customize context menu
        7. show
        '''
        self.readData()
        self.setLayout()
        self.plotData()
        self.setLabel()
        self.linkAxes()
        self.customMenu()
        self.view.showMaximized()

if __name__ == '__main__':
    # args
    parser = argparse.ArgumentParser(description='plot data from hrpsys log')
    parser.add_argument('-f', type=str, help='input file', metavar='file', required=True)
    parser.add_argument('--plot', type=str, help='plot configure file', metavar='file', required=True)
    parser.add_argument('--layout', type=str, help='layout configure file', metavar='file', required=True)
    parser.add_argument('-t', type=str, help='title', default=None)
    parser.set_defaults(feature=False)
    args = parser.parse_args()
    # main
    app = pyqtgraph.Qt.QtGui.QApplication([])
    a = DataloggerLogParser(args.f, args.plot, args.layout, args.t)
    a.main()
    pyqtgraph.Qt.QtGui.QApplication.instance().exec_()
