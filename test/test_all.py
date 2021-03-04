#!/usr/bin/python
#-*- coding:utf-8 -*-
import unittest
import pyqtgraph
from test_log_parser import *
from test_axis_range import *

if __name__ == '__main__':
    app = pyqtgraph.Qt.QtGui.QApplication([])
    try:
        unittest.main(verbosity=2)
    finally:
        del app
