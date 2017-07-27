#!/usr/bin/env python

import numpy
import metayaml
import multiprocessing
from log_plotter.plot_utils import readOneTopic, replaceRH
from log_plotter.graph_legend import expand_str_to_list


class LogParser(object):

    def __init__(self, fname, plot_conf, layout_conf, read_yaml = True):
        '''
        :param str fname: file name of log
        :param str/dict plot_conf: plot yaml file name / dict loaded from plot.yaml
        :param str/dict layout_conf: layout yaml file name / dcit loaded from layout.yaml
        '''
        self.fname = fname
        if read_yaml:
            self.plot_dict = metayaml.read(plot_conf)
            self.layout_dict = metayaml.read(layout_conf)["main"]
        else:
            self.plot_dict = plot_conf
            self.layout_dict = layout_conf
        # expand [0-33] => [0,1,2,...,33]
        for leg_info in self.plot_dict.values():
            for log_info in leg_info['data']:
                if type(log_info['column'][0]) == str:
                    log_info['column'] = expand_str_to_list(log_info['column'][0])
        for dict_title in self.layout_dict:
            for leg in self.layout_dict[dict_title]['legends']:
                if type(leg['id'][0]) == str:
                    leg['id'] = expand_str_to_list(leg['id'][0])
            self.layout_dict[dict_title].setdefault('newline', True)
            self.layout_dict[dict_title].setdefault('title', True)
            self.layout_dict[dict_title].setdefault('left_label', False)
            self.layout_dict[dict_title].setdefault('bottom_label', "time [s]")

        self.dataListDict = {}

    def readData(self):
        '''
        read log data from log files and store dataListDict
        # self.dataListDict[topic] = numpy.array([[t_0, x_0, y_0, ...],
        #                                         [t_1, x_1, y_1, ...],
        #                                         ...,
        #                                         [t_n, x_n, y_n, ...]])
        '''
        # get list fo used topic
        all_legends = reduce(lambda x, y: x + y, [self.layout_dict[title]['legends'] for title in self.layout_dict])
        used_keys = list(set([legend['key'] for legend in all_legends]))
        log_col_pairs = reduce(lambda x, y: x + y, [self.plot_dict[key]['data'] for key in used_keys])
        topic_list = list(set([log_col_pair['log'] for log_col_pair in log_col_pairs]))
        self._used_keys = used_keys
        self._topic_list = topic_list

        # store data in parallel
        fname_list = replaceRH([self.fname + '.' + ext for ext in topic_list])
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
            ss_tmp = self.dataListDict['RobotHardware0_servoState'][:, 1:]
            self.dataListDict['RobotHardware0_servoState'][:, 1:] = numpy.fromstring(ss_tmp.astype('i').tostring(), dtype='f').reshape(ss_tmp.shape)
        return self.dataListDict
