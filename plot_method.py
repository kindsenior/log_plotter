#!/usr/bin/env python
import numpy
import struct
import math

try:
    import pyqtgraph
except:
    print "please install pyqtgraph. see http://www.pyqtgraph.org/"
    sys.exit(1)

class PlotMethod(object):
    urata_len = 16
    color_list = pyqtgraph.functions.Colors.keys()

    @staticmethod
    def __plot_urata_servo(plot_item, times, data_dict, args, indices_list, arg_indices, cur_col, key, i, offset1, offset2=1):
        plot_item.plot(times, data_dict[args[0]][:, (PlotMethod.urata_len+1) * indices_list[arg_indices[0]][cur_col] + (offset1+offset2)],
                       pen=pyqtgraph.mkPen(PlotMethod.color_list[i], width=2), name=key)

    @staticmethod
    def plot_servostate(plot_item, times, data_dict, args, indices_list, arg_indices, cur_col, key, i):
        def RePack(x):
            val = struct.unpack('i', struct.pack('f', float(x)))[0]
            #calib = (val & 0x01)
            #servo = (val & 0x02) >> 1
            #power = (val & 0x04) >> 2
            state = (val & 0x0007fff8) >> 3
            #temp  = (val & 0xff000000) >> 24
            return state
        vfr = numpy.vectorize(RePack)
        plot_item.plot(times, vfr(data_dict[args[0]][:, (PlotMethod.urata_len+1) * indices_list[arg_indices[0]][cur_col] + (0+0)]),
                       pen=pyqtgraph.mkPen('r', width=2), name=key)
            
    @staticmethod
    def plot_commnormal(plot_item, times, data_dict, args, indices_list, arg_indices, cur_col, key, i):
        PlotMethod.__plot_urata_servo(plot_item, times, data_dict, args, indices_list, arg_indices, cur_col, key, i, 13)

    @staticmethod
    def plot_12V(plot_item, times, data_dict, args, indices_list, arg_indices, cur_col, key, i):
        PlotMethod.__plot_urata_servo(plot_item, times, data_dict, args, indices_list, arg_indices, cur_col, key, i, 9)

    @staticmethod
    def plot_80V(plot_item, times, data_dict, args, indices_list, arg_indices, cur_col, key, i):
        PlotMethod.__plot_urata_servo(plot_item, times, data_dict, args, indices_list, arg_indices, cur_col, key, i, 2)
    
    @staticmethod
    def plot_current(plot_item, times, data_dict, args, indices_list, arg_indices, cur_col, key, i):
        PlotMethod.__plot_urata_servo(plot_item, times, data_dict, args, indices_list, arg_indices, cur_col, key, i, 1)
    
    @staticmethod
    def plot_motor_temp(plot_item, times, data_dict, args, indices_list, arg_indices, cur_col, key, i):
        PlotMethod.__plot_urata_servo(plot_item, times, data_dict, args, indices_list, arg_indices, cur_col, key, i, 0)

    @staticmethod
    def plot_motor_outer_temp(plot_item, times, data_dict, args, indices_list, arg_indices, cur_col, key, i):
        PlotMethod.__plot_urata_servo(plot_item, times, data_dict, args, indices_list, arg_indices, cur_col, key, i, 7)

    @staticmethod
    def plot_abs_enc(plot_item, times, data_dict, args, indices_list, arg_indices, cur_col, key, i):
        plot_item.plot(times, [math.degrees(x) for x in data_dict[args[0]][:, (PlotMethod.urata_len+1) * indices_list[arg_indices[0]][cur_col] + (6+1)]],
                       pen=pyqtgraph.mkPen('g', width=2), name='abs - enc')

    @staticmethod
    def plot_rh_q_st_q(plot_item, times, data_dict, args, indices_list, arg_indices, cur_col, key, i):
        plot_item.plot(times, [math.degrees(x) for x in (data_dict[args[1]][:, indices_list[arg_indices[1]][cur_col]] - data_dict[args[0]][:, indices_list[arg_indices[0]][cur_col]])],
                       pen=pyqtgraph.mkPen('r', width=2), name=args[1]+" - rh_q")
    @staticmethod
    def plot_rad2deg(plot_item, times, data_dict, args, indices_list, arg_indices, cur_col, key, i):
        data_rad=data_dict[args[0]][:, indices_list[arg_indices[0]][cur_col]]
        data_deg=[math.degrees(x) for x in data_rad]
        plot_item.plot(times, data_deg,pen=pyqtgraph.mkPen(PlotMethod.color_list[i], width=(len(args)-i+3)), name=args[0])

    @staticmethod
    def plot_watt(plot_item, times, data_dict, args, indices_list, arg_indices, cur_col, key, i):
        joint_vel=data_dict[args[0]][:, indices_list[arg_indices[0]][cur_col]]
        joint_tau=data_dict[args[1]][:, indices_list[arg_indices[0]][cur_col]]
        watt=joint_vel*joint_tau
        plot_item.plot(times, watt,pen=pyqtgraph.mkPen(PlotMethod.color_list[i], width=len(args)-i), name=args[0], fillLevel=0, fillBrush=PlotMethod.color_list[i])

    @staticmethod
    def normal(plot_item, times, data_dict, args, indices_list, arg_indices, cur_col, key, i):
        plot_item.plot(times, data_dict[args[0]][:, indices_list[arg_indices[0]][cur_col]], pen=pyqtgraph.mkPen(PlotMethod.color_list[i], width=2), name=key)
