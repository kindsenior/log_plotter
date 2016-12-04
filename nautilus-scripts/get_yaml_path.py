#!/usr/bin/env python
# -*-coding: utf-8-*-
import sys
import os
import yaml
import functools
from pyqtgraph import QtGui
from pyqtgraph import QtCore

class PathSelector (QtGui.QGroupBox):
   def __init__(self, parent, group_name, button_name, default_path=None, stdout=False):
      '''
      :param widget parent: parent widget
      :param str group_name: name of this item displayed on left up
      :param str button_name: name displayed on button
      :param str default_path: default path to file
      '''
      self.parent = parent
      default_path = str(default_path)
      QtGui.QVBoxLayout.__init__(self, group_name)
      # make layouts
      vbox = QtGui.QVBoxLayout()
      hbox = QtGui.QHBoxLayout()
      # label and button
      self.label = QtGui.QLabel(default_path)
      self.button = QtGui.QPushButton(parent)
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
      d = QtGui.QFileDialog(self.parent)
      path = self.label.text()
      pathname = d.getOpenFileName(directory=os.path.dirname(str(path)))
      if not pathname == "":
         self.label.setText(pathname)

   def get_path(self):
      '''
      get current sellected path
      '''
      return str(self.label.text())

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
   def __init__(self, stdout=False):
      '''
      :param bool stdout: if True, print the path to plot.yaml and layout.yaml
      '''
      self.stdout = stdout
      plot_yaml_history, layout_yaml_history = self.read_path_history()
      self.window = QtGui.QWidget()
      vbox = QtGui.QVBoxLayout()

      script_root_dir = self.script_root_dir
      plot_yaml = PathSelector(self.window, 'plot.yaml', 'select', plot_yaml_history)
      layout_yaml = PathSelector(self.window, 'layout.yaml', 'select', layout_yaml_history)
      self.plot_yaml = plot_yaml
      self.layout_yaml = layout_yaml
      vbox.addWidget(plot_yaml)
      vbox.addWidget(layout_yaml)

      button = QtGui.QPushButton(self.window)
      button.setText('OK')
      vbox.addWidget(button)
      button.clicked.connect(self.quit_app)

      self.window.setLayout(vbox)
      self.window.setWindowTitle("PyQt Dialog demo")
      for btn in [plot_yaml.button, layout_yaml.button]:
         btn.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
      self.window.show()

   def main(self):
      '''
      :returns: path to plot.yaml and layout.yaml
      '''
      QtCore.QCoreApplication.instance().exec_()
      return (self.plot_yaml_path, self.layout_yaml_path)

   def quit_app(self):
      '''
      callback function when 'ok' button was pressed (end of this window)
      '''
      self.plot_yaml_path = self.plot_yaml.get_path()
      self.layout_yaml_path = self.layout_yaml.get_path()
      self.write_path_history(self.plot_yaml_path, self.layout_yaml_path)
      if self.stdout:
         sys.stdout.write('{} {}'.format(self.plot_yaml_path, self.layout_yaml_path))
      QtCore.QCoreApplication.instance().quit()

   def read_path_history(self):
      '''
      read history file and return the path.
      if history file was not found or invalid file was selected, return default path
      :returns: (plot.yaml, layout.yaml)
      '''
      script_root_dir = get_script_path()
      self.script_root_dir = script_root_dir
      historyfile = '{}/.log_plotter'.format(script_root_dir)
      try:
         with open(historyfile, 'r') as f:
            d = yaml.load(f)
         l = QtGui.QLabel()
         l.setText(str(d))
         l.show()
         plot_yaml_path = d['plot_yaml']
         layout_yaml_path = d['layout_yaml']
         plot_isYaml = os.path.basename(plot_yaml_path).split('.')[-1] == 'yaml'
         layout_isYaml = os.path.basename(layout_yaml_path).split('.')[-1] == 'yaml'
         if not os.path.exists(plot_yaml_path):
            raise ValueError('{} is not exist!'.format(plot_yaml_path))
         if not os.path.exists(layout_yaml_path):
            raise ValueError('{} is not exist!'.format(layout_yaml_path))
      except (ValueError, IOError):
         plot_isYaml =False
         layout_isYaml = False
      if not plot_isYaml:
         plot_yaml_path = '{}/{}'.format(script_root_dir, 'config/robot/jaxon/test.yaml')
      if not layout_isYaml:
         layout_yaml_path = '{}/{}'.format(script_root_dir, 'config/robot/jaxon/test-layout.yaml')
      self.plot_yaml_path = plot_yaml_path
      self.layout_yaml_path = layout_yaml_path
      return (plot_yaml_path, layout_yaml_path)

   def write_path_history(self, plot_yaml_path, layout_yaml_path):
      '''
      overwrite history file
      '''
      script_root_dir = self.script_root_dir
      historyfile = '{}/.log_plotter'.format(script_root_dir)
      d = {'plot_yaml':plot_yaml_path, 'layout_yaml': layout_yaml_path}
      with open(historyfile, 'w') as f:
         yaml.dump(d, f)

if __name__ == '__main__':
   app = QtGui.QApplication(sys.argv)
   m = MainDialog(stdout=True)
   m.main()
