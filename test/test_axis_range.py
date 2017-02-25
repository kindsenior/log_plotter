#!/usr/bin/python
#-*- coding:utf-8 -*-

import pyqtgraph
from numpy import isclose
import unittest.main
from unittest import TestCase
from test_util import log_plotter_exec

class TestLogPlotter(TestCase):
    def test_x_range(self):
        layout =u'''
main:
  graph of dummy:
    legends:
      - { key: dummy, id: [0] }
    yRange: {min: 7, max: 10}

'''
        a = log_plotter_exec(layout=layout,
                             plot_conf ='config/sample_plot.yaml',
                             fname = 'data/sample/sample_data',
                             eventLoop=10)
        # check xRange
        ax = a.view.ci.rows[0][0].getAxis('bottom')
        range_min = ax.range[0]
        range_max = ax.range[1]
        self.assertTrue(isclose(range_min, 0, atol=1), msg='bottom axis min is not correct. range_min={}'.format(range_min))
        self.assertTrue(isclose(range_max, 10,atol=1), msg='bottom axis max is not correct. range_max={}'.format(range_max))
        
        # check yRange
        ax = a.view.ci.rows[0][0].getAxis('left')
        range_min = ax.range[0]
        range_max = ax.range[1]
        self.assertTrue(isclose(range_min,  7, atol=1), msg='left axis min is not correct. range_min={}'.format(range_min))
        self.assertTrue(isclose(range_max, 10, atol=1), msg='left axis max is not correct. range_max={}'.format(range_max))

    def test_x_range2(self):
        layout =u'''
main:
  graph of dummy:
    legends:
      - { key: dummy, id: [0] }
    xRange: {min: 3, max: 10}
'''
        
        a = log_plotter_exec(layout=layout,
                             plot_conf ='config/sample_plot.yaml',
                             fname = 'data/sample/sample_data',
                             eventLoop=10)
        # check xRange
        ax = a.view.ci.rows[0][0].getAxis('bottom')
        range_min = ax.range[0]
        range_max = ax.range[1]
        self.assertTrue(isclose(range_min, 3, atol=1),  msg='left axis min is not correct. range_min={}'.format(range_min))
        self.assertTrue(isclose(range_max, 10, atol=1), msg='left axis max is not correct. range_max={}'.format(range_max))
        
        # check yRange
        ax = a.view.ci.rows[0][0].getAxis('left')
        range_min = ax.range[0]
        range_max = ax.range[1]
        self.assertTrue(isclose(range_min, 3, atol=1),  msg='left axis min is not correct. range_min={}'.format(range_min))
        self.assertTrue(isclose(range_max, 13, atol=1), msg='left axis max is not correct. range_max={}'.format(range_max))


    def test_x_range3(self):
        layout =u'''
main:
  graph of dummy:
    legends:
      - { key: dummy, id: [0] }
    xRange: {min: 3, max: 10, zero: True}
'''
        a = log_plotter_exec(layout=layout,
                             plot_conf ='config/sample_plot.yaml',
                             fname = 'data/sample/sample_data',
                             eventLoop=10)
        # check xRange
        ax = a.view.ci.rows[0][0].getAxis('bottom')
        range_min = ax.range[0]
        range_max = ax.range[1]
        self.assertTrue(isclose(range_min, 0, atol=1), msg='left axis min is not correct. range_min={}'.format(range_min)) 
        self.assertTrue(isclose(range_max, 7, atol=1), msg='left axis max is not correct. range_max={}'.format(range_max)) 
        
        # check yRange
        ax = a.view.ci.rows[0][0].getAxis('left')
        range_min = ax.range[0]
        range_max = ax.range[1]
        self.assertTrue(isclose(range_min, 3, atol=1),  msg='left axis min is not correct. range_min={}'.format(range_min))
        self.assertTrue(isclose(range_max, 13, atol=1), msg='left axis max is not correct. range_max={}'.format(range_max))

__all__ = ['TestLogPlotter']
        
if __name__ == '__main__':
    app = pyqtgraph.Qt.QtGui.QApplication([])
    try:
        unittest.main(verbosity=2)
    finally:
        del app
