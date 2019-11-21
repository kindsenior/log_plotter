#!/usr/bin/env python
import numpy
import struct
import math
import sys

try:
    import pyqtgraph
except:
    print("please install pyqtgraph. see http://www.pyqtgraph.org/")
    sys.exit(1)

class PlotMethod(object):
    urata_len = 16
    # color_list = pyqtgraph.functions.Colors.keys()
    # default color set on gnuplot 5.0
    color_list = ["9400D3", "009E73", "56B4E9", "E69F00", "F0E442", "0072B2", "E51E10", "0000FF"]
    linetypes = {
        "color": color_list * 5,
        "style": [pyqtgraph.QtCore.Qt.SolidLine] * len(color_list)
        + [pyqtgraph.QtCore.Qt.DotLine] * len(color_list)
        + [pyqtgraph.QtCore.Qt.DashLine] * len(color_list)
        + [pyqtgraph.QtCore.Qt.DashDotLine] * len(color_list)
        + [pyqtgraph.QtCore.Qt.DashDotDotLine] * len(color_list)
    }

    @staticmethod
    def __plot_urata_servo(plot_item, times, data_dict, logs, log_cols, cur_col, key, i, offset1, offset2=1):
        plot_item.plot(times, data_dict[logs[0]][:, (PlotMethod.urata_len+1) * log_cols[0] + (offset1+offset2)],
                       pen=pyqtgraph.mkPen(PlotMethod.linetypes["color"][i], width=2, style=PlotMethod.linetypes["style"][i]), name=key)

    @staticmethod
    def plot_servostate(plot_item, times, data_dict, logs, log_cols, cur_col, key, i):
        def RePack(x):
            val = struct.unpack('i', struct.pack('f', float(x)))[0]
            #calib = (val & 0x01)
            #servo = (val & 0x02) >> 1
            #power = (val & 0x04) >> 2
            state = (val & 0x0007fff8) >> 3
            #temp  = (val & 0xff000000) >> 24
            return state
        vfr = numpy.vectorize(RePack)
        plot_item.plot(times, vfr(data_dict[logs[0]][:, (PlotMethod.urata_len+1) * log_cols[0] + (0+0)]),
                       pen=pyqtgraph.mkPen(PlotMethod.linetypes["color"][i], width=2, style=PlotMethod.linetypes["style"][i]), name=key)

    @staticmethod
    def plot_commnormal(plot_item, times, data_dict, logs, log_cols, cur_col, key, i):
        PlotMethod.__plot_urata_servo(plot_item, times, data_dict, logs, log_cols, cur_col, key, i, 13)

    @staticmethod
    def plot_12V(plot_item, times, data_dict, logs, log_cols, cur_col, key, i):
        PlotMethod.__plot_urata_servo(plot_item, times, data_dict, logs, log_cols, cur_col, key, i, 9)

    @staticmethod
    def plot_80V(plot_item, times, data_dict, logs, log_cols, cur_col, key, i):
        PlotMethod.__plot_urata_servo(plot_item, times, data_dict, logs, log_cols, cur_col, key, i, 2)

    @staticmethod
    def plot_current(plot_item, times, data_dict, logs, log_cols, cur_col, key, i):
        PlotMethod.__plot_urata_servo(plot_item, times, data_dict, logs, log_cols, cur_col, key, i, 1)

    @staticmethod
    def plot_motor_temp(plot_item, times, data_dict, logs, log_cols, cur_col, key, i):
        PlotMethod.__plot_urata_servo(plot_item, times, data_dict, logs, log_cols, cur_col, key, i, 0)

    @staticmethod
    def plot_motor_outer_temp(plot_item, times, data_dict, logs, log_cols, cur_col, key, i):
        PlotMethod.__plot_urata_servo(plot_item, times, data_dict, logs, log_cols, cur_col, key, i, 7)

    @staticmethod
    def plot_pgain(plot_item, times, data_dict, logs, log_cols, cur_col, key, i):
        PlotMethod.__plot_urata_servo(plot_item, times, data_dict, logs, log_cols, cur_col, key, i, 10)

    @staticmethod
    def plot_dgain(plot_item, times, data_dict, logs, log_cols, cur_col, key, i):
        PlotMethod.__plot_urata_servo(plot_item, times, data_dict, logs, log_cols, cur_col, key, i, 11)

    @staticmethod
    def plot_enc(plot_item, times, data_dict, logs, log_cols, cur_col, key, i):
        plot_item.plot(times, [math.degrees(x) for x in data_dict[logs[0]][:, (PlotMethod.urata_len+1) * log_cols[0] + (4+1)]],
                       pen=pyqtgraph.mkPen(PlotMethod.linetypes["color"][i], width=2, style=PlotMethod.linetypes["style"][i]), name=key)

    @staticmethod
    def plot_abs_enc(plot_item, times, data_dict, logs, log_cols, cur_col, key, i):
        plot_item.plot(times, [math.degrees(x) for x in data_dict[logs[0]][:, (PlotMethod.urata_len+1) * log_cols[0] + (6+1)]],
                       pen=pyqtgraph.mkPen(PlotMethod.linetypes["color"][i], width=2, style=PlotMethod.linetypes["style"][i]), name=key)

    @staticmethod
    def plot_rh_q_st_q(plot_item, times, data_dict, logs, log_cols, cur_col, key, i):
        plot_item.plot(times, [math.degrees(x) for x in (data_dict[logs[1]][:, log_cols[1]] - data_dict[logs[0]][:, log_cols[0]])],
                       pen=pyqtgraph.mkPen(PlotMethod.linetypes["color"][i], width=2, style=PlotMethod.linetypes["style"][i]), name=key)

    @staticmethod
    def plot_rad2deg(plot_item, times, data_dict, logs, log_cols, cur_col, key, i):
        data_rad=data_dict[logs[0]][:, log_cols[0]]
        data_deg=[math.degrees(x) for x in data_rad]
        plot_item.plot(times, data_deg,pen=pyqtgraph.mkPen(PlotMethod.linetypes["color"][i], width=2, style=PlotMethod.linetypes["style"][i]), name=key)

    @staticmethod
    def plot_watt(plot_item, times, data_dict, logs, log_cols, cur_col, key, i):
        joint_vel=data_dict[logs[0]][:, log_cols[0]]
        joint_tau=data_dict[logs[1]][:, log_cols[1]]
        watt=joint_vel*joint_tau
        plot_item.plot(times, watt,pen=pyqtgraph.mkPen(PlotMethod.linetypes["color"][i], width=2, style=PlotMethod.linetypes["style"][i]), name=key, fillLevel=0, fillBrush=PlotMethod.linetypes["color"][i])

    @staticmethod
    def plot_rad2deg_vel(plot_item, times, data_dict, logs, log_cols, cur_col, key, i):
        data = [math.degrees(x) for x in numpy.diff(data_dict[logs[0]][:, log_cols[0]])/numpy.diff(times)]
        plot_item.plot(times, numpy.append(data,[0]), pen=pyqtgraph.mkPen(PlotMethod.linetypes["color"][i], width=2, style=PlotMethod.linetypes["style"][i]), name=key)

    @staticmethod
    def plot_rad2deg_vel_advanced(plot_item, times, data_dict, logs, log_cols, cur_col, key, i):
        cutoff = 20
        dt2pif = 0.002*2*math.pi*cutoff
        T = 0.01
        # T = 0.018
        T = 0.025
        tau = 1.0/(2*math.pi*cutoff)
        a = (T+tau)/tau
        command_vels = numpy.diff(data_dict[logs[0]][:, log_cols[0]])/numpy.diff(times)
        command_vel_prev = [command_vels[0]]
        ref_vel_prev = [command_vels[0]]
        ref_vel = [0]
        data = [math.degrees(ref_vel[0]) if ref_vel.__setitem__(0,command_vel*(a+dt2pif)/(1+dt2pif) - command_vel_prev[0]*a/(1+dt2pif) + ref_vel_prev[0]/(1+dt2pif)) or command_vel_prev.__setitem__(0,command_vel) or ref_vel_prev.__setitem__(0,ref_vel[0]) or True else -1 for command_vel in command_vels]
        plot_item.plot(times, numpy.append(data,[0]), pen=pyqtgraph.mkPen(PlotMethod.linetypes["color"][i], width=2, style=PlotMethod.linetypes["style"][i]), name=key)

    @staticmethod
    def plot_diff(plot_item, times, data_dict, logs, log_cols, cur_col, key, i):
        data_minuend = data_dict[logs[0]][:, log_cols[0]]
        data_subtrahend = data_dict[logs[1]][:, log_cols[1]]
        data = data_minuend - data_subtrahend
        plot_item.plot(times, data, pen=pyqtgraph.mkPen(PlotMethod.linetypes["color"][i], width=2, style=PlotMethod.linetypes["style"][i]), name=key)

    @staticmethod
    def plot_rad2deg_diff(plot_item, times, data_dict, logs, log_cols, cur_col, key, i):
        plot_item.plot(times, [math.degrees(x) for x in (data_dict[logs[1]][:, log_cols[1]] - data_dict[logs[0]][:, log_cols[0]])],
                       pen=pyqtgraph.mkPen(PlotMethod.linetypes["color"][i], width=2, style=PlotMethod.linetypes["style"][i]), name=key)

    @staticmethod
    def plot_comp(plot_item, times, data_dict, logs, log_cols, cur_col, key, i):
        plot_item.plot(times, data_dict[logs[0]][:, log_cols[0]],
                       pen=pyqtgraph.mkPen(PlotMethod.linetypes["color"][i], width=2, style=PlotMethod.linetypes["style"][i]), name=key)
        if log_cols[0] % 6 < 3: # position
            plot_item.setYRange(-0.025, +0.025) # compensation limit
        else: # rotation
            plot_item.setYRange(math.radians(-10), math.radians(+10)) # compensation limit

    @staticmethod
    def plot_COP(plot_item, times, data_dict, logs, log_cols, cur_col, key, i):
        # offset = log_cols[0]*6
        arg = logs[min(len(logs)-1,cur_col)]
        # f_z = data_dict[arg][:, offset+2]
        # tau_x = data_dict[arg][:, offset+3]
        # tau_y = data_dict[arg][:, offset+4]
        # plot_item.plot(times, -tau_y/f_z, pen=pyqtgraph.mkPen(PlotMethod.color_list[2*i], width=2, style=PlotMethod.linetypes["style"][i]), name=key)
        # plot_item.plot(times,  tau_x/f_z, pen=pyqtgraph.mkPen(PlotMethod.color_list[2*i+1], width=2, style=PlotMethod.linetypes["style"][i]), name=key)
        f_z = data_dict[logs[0]][:, log_cols[0]+2]
        if logs[0].find('rmfo'): f_z = -f_z
        tau_x = data_dict[logs[0]][:, log_cols[0]+3]
        if logs[0].find('rmfo'): tau_x = -tau_x
        tau_y = data_dict[logs[0]][:, log_cols[0]+4]
        plot_item.plot(times, -tau_y/f_z, pen=pyqtgraph.mkPen(PlotMethod.color_list[2*i], width=2, style=PlotMethod.linetypes["style"][i]), name=key+"_x")
        plot_item.plot(times,  tau_x/f_z, pen=pyqtgraph.mkPen(PlotMethod.color_list[2*i+1], width=2, style=PlotMethod.linetypes["style"][i]), name=key+"_y")


    @staticmethod
    def plot_inverse(plot_item, times, data_dict, logs, log_cols, cur_col, key, i):
        plot_item.plot(times, -data_dict[logs[0]][:, log_cols[0]], pen=pyqtgraph.mkPen(PlotMethod.linetypes["color"][i], width=2, style=PlotMethod.linetypes["style"][i]), name=key)

    @staticmethod
    def plot_time(plot_item, times, data_dict, logs, log_cols, cur_col, key, i):
        plot_item.plot(times, numpy.append([0], numpy.diff(times)), pen=pyqtgraph.mkPen(PlotMethod.linetypes["color"][i], width=2, style=PlotMethod.linetypes["style"][i]), name=key)

    @staticmethod
    def normal(plot_item, times, data_dict, logs, log_cols, cur_col, key, i):
        plot_item.plot(times, data_dict[logs[0]][:, log_cols[0]], pen=pyqtgraph.mkPen(PlotMethod.linetypes["color"][i], width=2, style=PlotMethod.linetypes["style"][i]), name=key)
