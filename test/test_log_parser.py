#!/usr/bin/python
#-*- coding:utf-8 -*-

import unittest.main
from unittest import TestCase
from log_plotter.log_parser import LogParser

class TestLogParser(TestCase):
    def test_from_file_joint(self):
        fname = 'data/jaxon_test_data/jaxon_test'
        plot_conf ='../config/robot/jaxon/jaxon_plot.yaml'
        layout_conf = 'config/jaxon_joint_layout.yaml'
        p = LogParser(fname, plot_conf, layout_conf)
        p.readData()
        # import pdb;pdb.set_trace();
        self.assertEqual(p.dataListDict.keys(), ['st_q'], msg='input file is not saved in LogParser')

    def test_from_file_watt(self):
        fname = 'data/jaxon_test_data/jaxon_test'
        plot_conf ='../config/robot/jaxon/jaxon_plot.yaml'
        layout_conf = 'config/jaxon_watt_layout.yaml'
        p = LogParser(fname, plot_conf, layout_conf)
        p.readData()
        # import pdb;pdb.set_trace();
        self.assertEqual(set(p.dataListDict.keys()), set(['RobotHardware0_dq','RobotHardware0_tau']), msg='input file is not saved in LogParser')

__all__ = ['TestLogParser']
        
if __name__ == '__main__':
    unittest.main(verbosity=2)

