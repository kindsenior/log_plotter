#!/usr/bin/env python

import numpy
import metayaml
import multiprocessing
from functools import reduce
from log_plotter.plot_utils import readOneTopic, readOneTopicZip, readOneTopicTar, replaceRHString
from log_plotter.graph_legend import expand_str_to_list
import zipfile
import tarfile
import os.path

class LogParser(object):

    def __init__(self, fname, plot_conf, layout_conf, read_yaml = True, start_idx = 0, data_length = 0):
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
        self.start_idx = start_idx
        self.data_length = data_length

        self.zip_file = None
        self.tar_file = None
        try:
            if zipfile.is_zipfile(fname):
                ##self.zip_file = zipfile.ZipFile(fname)
                self.zip_file = fname
                root_, ext_ = os.path.splitext(fname)
                self.fname = os.path.basename(root_)
                print('Open zip file: %s %s'%(self.zip_file, self.fname))
            elif tarfile.is_tarfile(fname):
                ##self.tar_file = tarfile.TarFile(fname)
                self.tar_file = fname
                root_, ext_ = os.path.splitext(fname)
                self.fname = os.path.basename(root_)
                ## hotfix for with statement
                tarfile.ExFileObject.__enter__ = lambda self_: self_
                tarfile.ExFileObject.__exit__ = lambda self_, a, b, c: None
                print('Open tar file: %s %s'%(self.tar_file, self.fname))
        except Exception as e:
            ## is_tarfile throw error
            pass

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
        fname_list = replaceRHString([self.fname + '.' + ext for ext in topic_list])
        read_func = readOneTopic
        if not self.zip_file is None:
            fname_list = map(lambda fn: [fn, self.start_idx, self.data_length, self.zip_file], fname_list) ## add start_idx, data_length
            read_func = readOneTopicZip
        elif not self.tar_file is None:
            fname_list = map(lambda fn: [fn, self.start_idx, self.data_length, self.tar_file], fname_list) ## add start_idx, data_length
            read_func = readOneTopicTar
        else:
            fname_list = map(lambda fn: [fn, self.start_idx, self.data_length], fname_list) ## add start_idx, data_length
        pl = multiprocessing.Pool()
        data_list = pl.map(read_func, fname_list)
        for topic, data in zip(topic_list, data_list):
            self.dataListDict[topic] = data
        # set the fastest time as 0
        min_time = min([data[0][0] for data in self.dataListDict.values() if data is not None])
        for log_name, data in self.dataListDict.items():
            if data is not None: self.dataListDict[log_name][:, 0] = data[:, 0] - min_time
        # convert servoState from int to float
        if 'RobotHardware0_servoState' in topic_list:
            if self.dataListDict['RobotHardware0_servoState'] is not None:
                ss_tmp = self.dataListDict['RobotHardware0_servoState'][:, 1:]
                self.dataListDict['RobotHardware0_servoState'][:, 1:] = numpy.fromstring(ss_tmp.astype('i').tostring(), dtype='f').reshape(ss_tmp.shape)
        return self.dataListDict
