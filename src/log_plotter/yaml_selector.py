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
   def __init__(self, group_name, button_name, default_path=None, stdout=False):
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
      # set parents
      hbox.addWidget(self.button)
      hbox.addWidget(self.label)
      vbox.addLayout(hbox)
      self.setLayout(vbox)
      self.button.clicked.connect(self.select_path)

   def select_path(self):
      '''
      callback function when 'select' button was pressed.
      '''
      d = QtGui.QFileDialog()
      pathname = d.getOpenFileName(directory=os.path.dirname(self.path))
      if not pathname == "":
         self.set_path(pathname)

   def set_path(self, pathname):
      self.label.setText(pathname)
      self.path = str(pathname)

def get_script_path():
   '''
   get absolute path to this python script file.
   '''
   import os
   import sys
   if sys.argv[0].split('/')[0] == '':
      return os.path.dirname(sys.argv[0])
   else:
      return os.path.realpath(os.path.dirname('{}/{}'.format(os.getcwd(), sys.argv[0]))) # /path/to/log-plotter

class MainDialog(object):
   '''
   get_yamls_path = MainDialog()
   plot_yaml_path, layout_yaml_path = get_yamls_path()
   '''
   def __init__(self):
      # set member
      self.plot_yaml_path = None
      self.layout_yaml_path = None
      self.script_root_dir = get_script_path()
      self.history_dir = os.environ['HOME']
      self.read_path_history()
      # layout
      ## widgets
      self.window = QtGui.QWidget()
      vbox = QtGui.QVBoxLayout()
      self.plot_yaml_selector = PathSelector('plot.yaml', 'select', self.plot_yaml_path)
      self.layout_yaml_selector = PathSelector('layout.yaml', 'select', self.layout_yaml_path)
      button = QtGui.QPushButton(self.window)
      button.setText('OK')
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
      historyfile = os.path.join(self.history_dir, '.log_plotter')
      history_data = {}
      try:
         with open(historyfile, 'r') as f:
            history_data.update(yaml.load(f))
      finally:
         default_paths = {
            'plot_yaml':'{}/{}'.format(self.script_root_dir, 'config/robot/jaxon/test.yaml'),
            'layout_yaml':'{}/{}'.format(self.script_root_dir, 'config/robot/jaxon/test-layout.yaml')
         }
         for path_key in default_paths:
            if not os.path.basename(history_data.get(path_key)).split('.')[-1] == 'yaml':
               history_data[path_key] = default_paths[path_key]
            if not os.path.exists(history_data[path_key]):
               print('{} is not exist!'.format(history_data[path_key]))
               history_data[path_key] = default_paths[path_key]
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
      script_root_dir = self.script_root_dir
      historyfile = '{}/.log_plotter'.format(self.history_dir)
      d = {'plot_yaml':plot_yaml_path, 'layout_yaml': layout_yaml_path}
      with open(historyfile, 'w') as f:
         yaml.dump(d, f)

if __name__ == '__main__':
   app = QtGui.QApplication([])
   get_yamls_path = MainDialog()
   plot_yaml_path, layout_yaml_path = get_yamls_path()
   print plot_yaml_path, layout_yaml_path
