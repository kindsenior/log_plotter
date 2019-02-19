#!/usr/bin/env python
# -*-coding: utf-8-*-
import sys
import os
import yaml
import functools
from pyqtgraph import QtGui
from pyqtgraph import QtCore

class PathSelector (QtGui.QGroupBox):
   '''
   :members: path (path/to/yaml)
   '''
   def __init__(self, group_name, button_name, default_path=None, stdout=False, filter="yaml (*.yaml)"):
      '''
      ex:
      PathSelector('plot.yaml', 'select', '/path/to/default/plot.yaml')
      :param widget parent: parent widget
      :param str group_name: name of this item displayed on left up
      :param str button_name: name displayed on button
      :param str default_path: default path to file
      '''
      self.path = str(default_path)
      QtGui.QVBoxLayout.__init__(self, group_name)
      # make layouts
      vbox = QtGui.QVBoxLayout()
      hbox = QtGui.QHBoxLayout()
      # label and button
      self.label = QtGui.QLabel(self.path)
      self.button = QtGui.QPushButton()
      self.button.setText(button_name)
      self.button.setAutoDefault(True)
      # set parents
      hbox.addWidget(self.button)
      hbox.addWidget(self.label)
      vbox.addLayout(hbox)
      self.setLayout(vbox)
      self.button.clicked.connect(functools.partial(self.select_path, filter))

   def select_path(self, filter):
      '''
      callback function when 'select' button was pressed.
      '''
      d = QtGui.QFileDialog()
      # Compatible with Qt5 and Qt4
      if QtCore.QT_VERSION >= 0x050000:
         pathname, _filter = d.getOpenFileName(directory=os.path.dirname(self.path), filter=filter)
      else:
         pathname = d.getOpenFileName(directory=os.path.dirname(self.path), filter=filter)
      if not pathname == "":
         self.set_path(pathname)

   def set_path(self, pathname):
      self.label.setText(pathname)
      self.path = str(pathname)

def get_module_dir():
   '''
   get absolute path to log_plotter module for history file.
   when in catkin workspace, return package dir.
   when not in catkin workspace, return HOME dir (we cannot write file in /usr/local/lib/python...)
   '''
   import os
   import sys
   try:
      import roslib
      return roslib.packages.get_pkg_dir('log_plotter')
   except:
      return os.environ['HOME']

class MainDialog(object):
   '''
   get_yamls_path = MainDialog()
   plot_yaml_path, layout_yaml_path = get_yamls_path()
   '''
   def __init__(self):
      # set member
      self.plot_yaml_path = None
      self.layout_yaml_path = None
      self.module_dir = get_module_dir()
      self.history_path = os.path.join(self.module_dir, '.log_plotter')
      self.read_path_history()
      # layout
      ## widgets
      self.window = QtGui.QWidget()
      vbox = QtGui.QVBoxLayout()
      self.plot_yaml_selector = PathSelector('plot.yaml', 'select', self.plot_yaml_path, filter="_plot.yaml (*_plot.yaml)")
      self.layout_yaml_selector = PathSelector('layout.yaml', 'select', self.layout_yaml_path, filter="_layout.yaml (*_layout.yaml)")
      button = QtGui.QPushButton(self.window)
      button.setText('OK')
      button.setAutoDefault(True);
      ## set layout
      vbox.addWidget(self.plot_yaml_selector)
      vbox.addWidget(self.layout_yaml_selector)
      vbox.addWidget(button)
      button.clicked.connect(self.quit_app)
      self.window.setLayout(vbox)
      self.window.setWindowTitle("log_plotter")
      # connect
      for btn in [self.plot_yaml_selector.button, self.layout_yaml_selector.button]:
         btn.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)

   def __call__(self):
      self.window.show()
      QtCore.QCoreApplication.instance().exec_()
      return (self.plot_yaml_path, self.layout_yaml_path)

   def read_path_history(self):
      '''
      read history file and return the path.
      if history file was not found or invalid file was selected, return default path
      :returns: (plot.yaml, layout.yaml)
      '''
      history_data = {}
      default_paths = {
         'plot_yaml':'{}/{}'.format(self.module_dir, 'config/robot/jaxon/test.yaml'),
         'layout_yaml':'{}/{}'.format(self.module_dir, 'config/robot/jaxon/test-layout.yaml')
      }
      history_data.update(default_paths)
      try:
         with open(self.history_path, 'r') as f:
            history_data.update(yaml.load(f))
      except:
         pass
      self.plot_yaml_path = history_data['plot_yaml']
      self.layout_yaml_path = history_data['layout_yaml']

   def quit_app(self):
      '''
      callback function when 'ok' button was pressed (end of this window)
      '''
      self.plot_yaml_path = self.plot_yaml_selector.path
      self.layout_yaml_path = self.layout_yaml_selector.path
      self.write_path_history(self.plot_yaml_path, self.layout_yaml_path)
      self.window.close()
      QtCore.QCoreApplication.instance().quit()

   def write_path_history(self, plot_yaml_path, layout_yaml_path):
      '''
      overwrite history file
      '''
      d = {'plot_yaml':plot_yaml_path, 'layout_yaml': layout_yaml_path}
      with open(self.history_path, 'w') as f:
         yaml.dump(d, f)

if __name__ == '__main__':
   app = QtGui.QApplication([])
   get_yamls_path = MainDialog()
   plot_yaml_path, layout_yaml_path = get_yamls_path()
   print(plot_yaml_path, layout_yaml_path)
