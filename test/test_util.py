import pyqtgraph
from log_plotter.datalogger_plotter_with_pyqtgraph import LogPlotter

def log_plotter_exec(layout = None, plot = None,
                     layout_conf = None, plot_conf = None,
                     fname = None, title = 'test log_lotter',
                     run=True, eventLoop=0):
    '''
    generate and run log_plotter from str or conf file.
    layout or layout_conf is necessary.
    plot or plot_conf is necessary.

    :param str layout: contents of layout.yaml
    :param str plot: contents of plot.yaml
    :param str layout_conf: path to layout.yaml
    :param str plot_conf: path to plot.yaml
    :param str fname: path to log file
    :param str title: graph window title
    :param bool run: if True, run LogPlotter.main()
    '''
    if layout is not None and layout_conf is None:
        layout_conf = '/tmp/tmp_layout.yaml'
        with open(layout_conf, 'w') as f:
            f.write(layout)
    if plot is not None and plot_conf is None:
        plot_conf = '/tmp/tmp_plot.yaml'
        with open(layout_conf, 'w') as f:
            f.write(layout)
    # import pdb;pdb.set_trace()
    a = LogPlotter(fname, plot_conf, layout_conf)
    if run:
        a.main()
        app = pyqtgraph.QtCore.QCoreApplication.instance()
        [app.processEvents() for i in range(eventLoop)]
    return a
