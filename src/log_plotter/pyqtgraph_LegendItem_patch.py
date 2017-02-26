import pyqtgraph.graphicsItems
from pyqtgraph.Qt import QtGui, QtCore
from pyqtgraph.graphicsItems.GraphicsWidget import GraphicsWidget
from pyqtgraph import functions as fn
from pyqtgraph.graphicsItems.ScatterPlotItem import ScatterPlotItem, drawSymbol
from pyqtgraph.graphicsItems.PlotDataItem import PlotDataItem

# set legend forefround white
def white_foreground_legend_item_paint(legend_item, p, *args):
    p.setPen(fn.mkPen(0,0,0,255, width = 1)) # r,g,b,alpha
    p.setBrush(fn.mkBrush(255,255,255,255))
    p.drawRect(legend_item.boundingRect())

# set legend, ItemSample horizontal
class HorizenLegend(GraphicsWidget):
    """ Class responsible for drawing a single item in a LegendItem (sans label).

    This may be subclassed to draw custom graphics in a Legend.
    """
    ## Todo: make this more generic; let each item decide how it should be represented.
    def __init__(self, item):
        GraphicsWidget.__init__(self)
        self.item = item

    def boundingRect(self):
        return QtCore.QRectF(0, 0, 20, 20)

    def paint(self, p, *args):
        #p.setRenderHint(p.Antialiasing)  # only if the data is antialiased.
        opts = self.item.opts

        if opts.get('fillLevel',None) is not None and opts.get('fillBrush',None) is not None:
            p.setBrush(fn.mkBrush(opts['fillBrush']))
            p.setPen(fn.mkPen(None))
            p.drawPolygon(QtGui.QPolygonF([QtCore.QPointF(2,18), QtCore.QPointF(18,2), QtCore.QPointF(18,18)]))

        if not isinstance(self.item, ScatterPlotItem):
            p.setPen(fn.mkPen(opts['pen']))
            p.drawLine(2, 10, 18, 10)

        symbol = opts.get('symbol', None)
        if symbol is not None:
            if isinstance(self.item, PlotDataItem):
                opts = self.item.scatter.opts

            pen = fn.mkPen(opts['pen'])
            brush = fn.mkBrush(opts['brush'])
            size = opts['size']

            p.translate(10,10)
            path = drawSymbol(p, symbol, size, pen, brush)

# avoid LegendItem cover ItemSample
def LegendItem_updateSize(self):
    if self.size is not None:
        return
    margins = self.layout.getContentsMargins()
    height = margins[1] + margins[3]
    width = margins[0] + margins[2] + self.layout.horizontalSpacing()
    #print("-------")
    for sample, label in self.items:
        height += max(sample.height(), label.height()) + self.layout.verticalSpacing()
        width = max(width, sample.width()+label.width())
        #print(width, height)
    height -= self.layout.verticalSpacing()
    #print width, height
    # self.setGeometry(0, 0, width+25, height)
    self.setGeometry(0, 0, width, height)

# set default value in LegendItem
LegendItem_init_orig = pyqtgraph.graphicsItems.LegendItem.LegendItem.__init__
def LegendItem_init(self, *args, **kwargs):
    LegendItem_init_orig(self, *args, **kwargs)
    self.layout.setContentsMargins(9.,0.,9.,0.)
    self.layout.setVerticalSpacing(-5.)
    self.layout.setHorizontalSpacing(25)

# justify left for legend label
from pyqtgraph.graphicsItems.LabelItem import LabelItem
def LegendItem_addItem(self, item, name):
    label = LabelItem(name, justify='left', color='000000')
    if isinstance(item, pyqtgraph.graphicsItems.LegendItem.ItemSample):
        sample = item
    else:
        sample = pyqtgraph.graphicsItems.LegendItem.ItemSample(item)
    row = self.layout.rowCount()
    self.items.append((sample, label))
    self.layout.addItem(sample, row, 0)
    self.layout.addItem(label, row, 1)
    self.updateSize()

pyqtgraph.graphicsItems.LegendItem.LegendItem.__init__ = LegendItem_init
pyqtgraph.graphicsItems.LegendItem.LegendItem.paint = white_foreground_legend_item_paint
pyqtgraph.graphicsItems.LegendItem.LegendItem.updateSize = LegendItem_updateSize
pyqtgraph.graphicsItems.LegendItem.LegendItem.addItem = LegendItem_addItem
pyqtgraph.graphicsItems.LegendItem.ItemSample = HorizenLegend
