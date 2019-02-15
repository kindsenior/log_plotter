import sys
import numpy
import functools
from pyqtgraph import QtGui
from pyqtgraph import QtCore

class GraphSize(QtGui.QWidget):
   sig_graph_width = QtCore.pyqtSignal(int)
   sig_graph_height = QtCore.pyqtSignal(int)
   def __init__(self, plot_item, plot_item_parent):
      QtGui.QWidget.__init__(self)
      self.layout = QtGui.QGridLayout()
      self.plot_item = plot_item
      self.plot_item_parent = plot_item_parent
      self.rows = {}
      vb = self.plot_item.getViewBox()
      # graph size
      name = 'graph width'
      _, spinbox, check = self.add_row(name, "all")
      spinbox.setKeyboardTracking(False)
      spinbox.setValue(self.plot_item.width())
      spinbox.valueChanged.connect(functools.partial(self.set_graph_width, spinbox, check))
      vb.sigResized.connect(functools.partial(self.get_graph_width, spinbox))
      name = 'graph height'
      _, spinbox, check = self.add_row(name, "all")
      spinbox.setKeyboardTracking(False)
      spinbox.setValue(self.plot_item.height())
      spinbox.valueChanged.connect(functools.partial(self.set_graph_height, spinbox, check))
      vb.sigResized.connect(functools.partial(self.get_graph_height, spinbox))
      name = 'window width'
      _, spinbox = self.add_row(name)
      spinbox.setKeyboardTracking(False)
      spinbox.setValue(self.plot_item_parent.width())
      spinbox.valueChanged.connect(functools.partial(self.set_layout_width, spinbox))
      name = 'window height'
      _, spinbox = self.add_row(name)
      spinbox.setKeyboardTracking(False)
      spinbox.setValue(self.plot_item_parent.height())
      spinbox.valueChanged.connect(functools.partial(self.set_layout_height, spinbox))

      self.setLayout(self.layout)
      for plot_item in plot_item_parent.ci.items.keys():
         self.sig_graph_height.connect(plot_item.setFixedHeight)
         self.sig_graph_width.connect(plot_item.setFixedWidth)

   def add_row(self, name, checkbox_name=None):
      current_row = self.layout.rowCount()
      if self.layout.count != 0:
         current_row +=1
      l = QtGui.QLabel(name) # graph width label
      sp = QtGui.QSpinBox()     # graph width spinbox
      sp.setMaximum(max(QtGui.QApplication.desktop().size().width(),
                        QtGui.QApplication.desktop().size().height()))
      self.rows[name] = (l, sp)
      self.layout.addWidget(l,current_row, 0)
      self.layout.addWidget(sp,current_row, 1)
      if checkbox_name is not None:
         l_check = QtGui.QLabel(checkbox_name)
         check = QtGui.QCheckBox()
         self.layout.addWidget(l_check, current_row, 2)
         self.layout.addWidget(check, current_row, 3)
         return l, sp, check
      return l, sp

   def set_graph_width(self, spinbox, checkbox=None):
      val = spinbox.value()
      self.plot_item.setFixedWidth(val)
      if (checkbox is not None) and (checkbox.checkState() != 0):
         self.sig_graph_width.emit(val)

   def get_graph_width(self, spinbox):
      spinbox.blockSignals(True)
      spinbox.setValue(self.plot_item.width())
      spinbox.blockSignals(False)

   def set_graph_height(self, spinbox, checkbox=None):
      val = spinbox.value()
      self.plot_item.setFixedHeight(val)
      if (checkbox is not None) and (checkbox.checkState() != 0):
         self.sig_graph_height.emit(val)

   def get_graph_height(self, spinbox):
      spinbox.blockSignals(True)
      spinbox.setValue(self.plot_item.height())
      spinbox.blockSignals(False)

   def set_layout_width(self, spinbox):
      val = spinbox.value()
      self.plot_item_parent.setFixedWidth(val)

   def set_layout_height(self, spinbox):
      val = spinbox.value()
      self.plot_item_parent.setFixedHeight(val)
