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


class DataloggerLogParserController:
    def __init__(self, fname, yname, title):
        self.fname = fname
        with open(yname, "r") as f:
            self.plot_dic = yaml.load(f)
        # setup view
        self.view = pyqtgraph.GraphicsLayoutWidget()
        self.view.setBackground('w')
        self.view.setWindowTitle(title if title else fname.split('/')[-1])
        # self.dateListDict is set by self.readData()
        self.dataListDict = {}
        # back up for plot items
        self.plotItemOrig = {}

    @my_time
    def readData(self):
        '''
        read log data from log files and store dataListDict
        # self.dataListDict[topic] = numpy.array([[t_0, x_0, y_0, ...],
        #                                         [t_1, x_1, y_1, ...],
        #                                         ...,
        #                                         [t_n, x_n, y_n, ...]])
        '''
        log_list_list = [x[1]["log"] for x in self.plot_dic.items()]
        duplicated_list = reduce(lambda x, y: x + y, log_list_list)
        topic_list = list(set(duplicated_list))
        # store data in parallel
        fname_list = [self.fname+'.'+tpc for tpc in topic_list]
        pl = multiprocessing.Pool()
        data_list = pl.map(readOneTopic, fname_list)
        for tpc, data in zip(topic_list, data_list):
            self.dataListDict[tpc] = data
        # set the fastest time as 0
        min_time = min([self.dataListDict[tpc][0][0] for tpc in topic_list])
        for tpc in topic_list:
            raw_time = self.dataListDict[tpc][:, 0]
            self.dataListDict[tpc][:, 0] = [x - min_time for x in raw_time]
        # fix servoState
        if 'RobotHardware0_servoState' in topic_list:
            def ssConverter(x):
                return struct.unpack('f', struct.pack('i', int(x)))[0]
            vf = numpy.vectorize(ssConverter)
            ss_tmp = self.dataListDict['RobotHardware0_servoState'][:, 1:]
            self.dataListDict['RobotHardware0_servoState'][:, 1:] = vf(ss_tmp)

    @my_time
    def setLayout(self):
        '''
        set layout of view according to self.plot_dic
        '''
        row = 0
        for x in self.plot_dic.items():
            for fld in x[1]["field"]:
                for c in range(len(fld)):
                    self.view.addPlot()
                self.view.nextRow()
                row += 1

    @my_time
    def plotData(self):
        '''
        plot
        '''
        color_list = pyqtgraph.functions.Colors.keys()
        cur_row = 0
        for plot in self.plot_dic.items(): # plot : ('joint_velocity', {'field':[[0,1],[2,3]], 'log':['rh_q', 'st_q']})
            title = plot[0]
            cur_fields = plot[1]['field']  # [[0,1],[2,3]]
            cur_logs = plot[1]['log']      # ['rh_q', 'st_q']
            for cf in cur_fields: # cf : [0,1]
                for i, cl in enumerate(cur_logs): # cl : 'rh_q'
                    cur_data = self.dataListDict[cl][:, 1:]
                    cur_tm = self.dataListDict[cl][:, 0]
                    for cur_col in cf: # cur_col : 0 / 1 / 2 / 3 ...
                        cur_item = self.view.ci.rows[cur_row][cur_col-cf[0]]
                        cur_item.setTitle(title+" "+str(cur_col))
                        cur_item.showGrid(x=True, y=True)
                        if i == 0: # we should call addLegend once a plot item
                            cur_item.addLegend(offset=(0, 0))
                        # plot
                        if cl == 'RobotHardware0_servoState':
                            urata_len = 16
                            if title == "ServoState":
                                def RePack(x):
                                    val = struct.unpack('i', struct.pack('f', float(x)))[0]
                                    #calib = (val & 0x01)
                                    #servo = (val & 0x02) >> 1
                                    #power = (val & 0x04) >> 2
                                    state = (val & 0x0007fff8) >> 3
                                    #temp  = (val & 0xff000000) >> 24
                                    return state
                                vfr = numpy.vectorize(RePack)
                                cur_item.plot(cur_tm, vfr(cur_data[:, (urata_len+1) * cur_col + (0+0)]),
                                              pen=pyqtgraph.mkPen('r', width=2), name='ServoState')
                            if title == "CommNormal":
                                cur_item.plot(cur_tm, cur_data[:, (urata_len+1) * cur_col + (13+1)],
                                              pen=pyqtgraph.mkPen('r', width=2), name='CommNormal')
                            if title == "12V":
                                cur_item.plot(cur_tm, cur_data[:, (urata_len+1) * cur_col + (9+1)],
                                              pen=pyqtgraph.mkPen('r', width=2), name='12V')
                            elif title == "80V":
                                cur_item.plot(cur_tm, cur_data[:, (urata_len+1) * cur_col + (2+1)],
                                              pen=pyqtgraph.mkPen('g', width=2), name='80V')
                            elif title == "current":
                                cur_item.plot(cur_tm, cur_data[:, (urata_len+1) * cur_col + (1+1)],
                                              pen=pyqtgraph.mkPen('b', width=2), name='current')
                            elif title == "temperature":
                                cur_item.plot(cur_tm, cur_data[:, (urata_len+1) * cur_col + (0+1)],
                                              pen=pyqtgraph.mkPen('r', width=2), name='motor_temp')
                                cur_item.plot(cur_tm, cur_data[:, (urata_len+1) * cur_col + (7+1)],
                                              pen=pyqtgraph.mkPen('g', width=1), name='motor_outer_temp')
                            elif title == "tracking":
                                cur_item.plot(cur_tm, [math.degrees(x) for x in cur_data[:, (urata_len+1) * cur_col + (6+1)]],
                                              pen=pyqtgraph.mkPen('g', width=2), name='abs - enc')
                        elif title == "tracking":
                            if cl == "RobotHardware0_q":
                                cur_item.plot(cur_tm, [math.degrees(x) for x in (self.dataListDict['st_q'][:, 1:][:, cur_col] - cur_data[:, cur_col])],
                                              pen=pyqtgraph.mkPen('r', width=2), name="st_q - rh_q")
                            else:
                                pass
                        elif title == "joint_angle" or title == "joint_velocity" or title == "attitude":
                            cur_item.plot(cur_tm, [math.degrees(x) for x in cur_data[:, cur_col]],
                                          pen=pyqtgraph.mkPen(color_list[i], width=len(cur_logs)-i), name=cl)
                        elif title == "watt":
                            if cl == "RobotHardware0_dq":
                                cur_item.plot(cur_tm, [math.degrees(x) for x in self.dataListDict['RobotHardware0_tau'][:, (cur_col+1):] * cur_data[:, cur_col]],
                                              pen=pyqtgraph.mkPen(color_list[i], width=len(cur_logs)-i), name=cl, fillLevel=0, fillBrush=color_list[i])
                            else:
                                pass
                        elif title == "imu":
                            mod3 = cur_col % 3
                            if cl == 'RobotHardware0_gsensor':
                                self.view.ci.rows[cur_row][0].plot(cur_tm, cur_data[:, cur_col],
                                                                   pen=pyqtgraph.mkPen(color_list[mod3], width=3-mod3), name=['x', 'y', 'z'][mod3])
                            elif cl == 'RobotHardware0_gyrometer':
                                self.view.ci.rows[cur_row][1].plot(cur_tm, cur_data[:, cur_col],
                                                                   pen=pyqtgraph.mkPen(color_list[mod3], width=3-mod3), name=['x', 'y', 'z'][mod3])
                        elif title == "comp":
                            cur_item.plot(cur_tm, cur_data[:, cur_col],
                                          pen=pyqtgraph.mkPen(color_list[i], width=len(cur_logs)-i), name=cl)
                            if cur_col % 6 < 3: # position
                                cur_item.setYRange(-0.025, +0.025) # compensation limit
                            else: # rotation
                                cur_item.setYRange(math.radians(-10), math.radians(+10)) # compensation limit
                        else:
                            cur_item.plot(cur_tm, cur_data[:, cur_col],
                                          pen=pyqtgraph.mkPen(color_list[i], width=len(cur_logs)-i), name=cl)
                # increase current row
                cur_row = cur_row + 1

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
    parser.add_argument('--conf', type=str, help='configure file', metavar='file', required=True)
    parser.add_argument('-t', type=str, help='title', default=None)
    parser.set_defaults(feature=False)
    args = parser.parse_args()
    # main
    app = pyqtgraph.Qt.QtGui.QApplication([])
    a = DataloggerLogParserController(args.f, args.conf, args.t)
    a.main()
    pyqtgraph.Qt.QtGui.QApplication.instance().exec_()
