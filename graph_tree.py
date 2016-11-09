# -*- coding:utf-8 -*-

'''
# classes
Multiarray:
utililty class for multi array supporting array[:,0] etc.

GraphGroupTree:
manage the all subplots. 2d list of graphs.

GraphGroup:
1d list of graphs belonging to the sampe group. (row of grpahs in window)

GraphInfo:
representing one graph. array of legends.

LegendInfo:
representing one legend. how_to_plot is a dictionary describing the data to plot one legend.

# structure
- GraphGroupTree
    - GraphGroup
        - GraphInfo
            -LegendInfo
            -LegendInfo
        - GraphInfo
            -LegendInfo
            -LegendInfo
            -LegendInfo
    - GraphGroup
        - GraphInfo
            -LegendInfo
            -LegendInfo

'''

class MultiArray(list):
    def __init___(self, array):
        list.__init__(self,array)
        return self

    def __getitem__(self, args):
        if type(args) == tuple:
            if type(args[0]) == int:
                try:
                    return self[args[0]].__getitem__(*args[1:])
                except:
                    raise IndexError
            else:
                tmp_list = MultiArray([])
                for row in self[args[0]]:
                    tmp = row[args[1]]
                    tmp_list.append(tmp)
                return tmp_list
        else:
            tmp = list.__getitem__(self, args)
            if issubclass(type(tmp), MultiArray):
                return tmp
            if issubclass(type(tmp), list):
                return MultiArray(tmp)
            else:
                return tmp

    def __repr__(self):
        _repr = ""
        class_name = str(self.__class__.__name__) + ": "
        _repr += str(class_name)
        if hasattr(self, 'name') and self.name != None:
            _repr += str(self.name) + " "
        _repr += "["
        max_show = 3
        max_show = min(max_show, max(max_show, len(self)-2), len(self))
        for i in range(max_show):
            _repr += str(self[i].name) if hasattr(self[i], 'name') else str(self[i])
            if i < max_show -1:
                _repr += ", "
        if max_show < len(self):
            _repr += ",...,"
            _repr += str(self[-1].name) if hasattr(self[-1], 'name') else str(self[-1])
        _repr += "]"
        return _repr[:100]

class PlotDictInterface(object):
    def __init__(self):
        self.plot_dict = self.parent.plot_dict

class RowColInterface(object):
    _row = None
    _col = None
    _children =[]
    max_row = 0
    max_col = 0
    def __init__(self):
        self.__row = None
        self.__col = None
    def row(self):
        return self.__row
    def col(self):
        return self.__col
    def loc(self):
        return self.__row, self.__col
    def put(self):
        try:
            assert(RowColInterface._col != None)
        except:
            raise Exception('please call resetManager() before you first call put()!')
        try:
            assert(self not in RowColInterface._children)
        except:
            raise Exception('do not call put() twice or more!')
        RowColInterface._col += 1
        self.__col = RowColInterface._col
        self.__row = RowColInterface._row
        RowColInterface._children.append(self)
        if self.__row > RowColInterface.max_row: RowColInterface.max_row += self.__row
        if self.__col > RowColInterface.max_col: RowColInterface.max_col += self.__col
        return self.__row, self.__col
    @staticmethod
    def newline():
        RowColInterface._row += 1
        RowColInterface._col = -1
    @staticmethod
    def resetManager():
        RowColInterface._row = 0
        RowColInterface._col = -1

class GraphGroupTree(MultiArray):
    '''
    all the graph
    '''
    def __init__(self, layout_list, plot_dict, name = None):
        '''
        layout_list: layout.yaml (list)
        plot_dict: plot.yaml (dict)
        this graph know each graph groups.
        '''
        self.layout_list = layout_list
        self.plot_dict = plot_dict
        self.name = name
        member = [GraphGroup(self, i) for i,_ in enumerate(self.layout_list)]
        MultiArray.__init__(self, member)
        RowColInterface.resetManager()
        for gg in self:
            for g in gg:
                g.put()
            if not (gg.layout.has_key('newline') and gg.layout['newline'] == False ):
                RowColInterface.newline()

    def complement_layout_list():
        pass

    def complement_plot_dict():
        pass

class GraphGroup(MultiArray, PlotDictInterface):
    '''
    graphs in line
    '''
    def __init__(self, parent, idx):
        '''
        parent_tree: parent tree
        layout: one member from layout.yaml
        this class is list of graphs belonging to the same graph group
        '''
        self.parent = parent
        self._id = idx
        self.layout = self.parent.layout_list[self._id]
        self.name = self.layout['group']
        PlotDictInterface.__init__(self)
        col_max_len = max([len(item) for item in self.layout['index']])
        members = [GraphInfo(self, i) for i in range(col_max_len)]
        MultiArray.__init__(self, members)

class GraphInfo(MultiArray, PlotDictInterface, RowColInterface):
    '''
    each graph
    '''
    def __init__(self, parent, idx):
        self.parent = parent
        self._id = idx
        self.layout = self.parent.layout.copy()
        self.layout['index'] = [item[self._id] for item in self.parent.layout['index']]
        self.name = str('{}[{}]'.format(self.parent.name, self.layout['index'][0]))
        PlotDictInterface.__init__(self)
        RowColInterface.__init__(self)
        members = [LegendInfo(self, legend_id) for legend_id, _ in enumerate(self.layout['index'])]
        MultiArray.__init__(self, members)

class LegendInfo(PlotDictInterface):
    '''
    each legend in graph
    '''
    def __init__(self, parent, idx):
        self.parent = parent
        self.index = idx
        self.layout = self.parent.layout.copy()
        self.layout['name'] = self.parent.layout['name'][self.index]
        self.layout['key'] = self.parent.layout['key'][self.index]
        self.layout['index'] = self.parent.layout['index'][self.index]
        self.name = self.layout['name']
        PlotDictInterface.__init__(self)
        self.how_to_plot = self.lookup_plot_dict(self.plot_dict)

    def lookup_plot_dict(self, plot_dict):
        key = self.layout['key']
        index = self.layout['index']
        how_to_plot = plot_dict[key].copy()
        how_to_plot['index'] = [item[index] for item in plot_dict[key]['index']]
        return how_to_plot

    def __repr__(self):
        return "{}: {}".format(str(self.__class__.__name__), str(self.name))

def test_GraphTree():
    layout_list = a.layout_list
    plot_dict = a.plot_dict
    gt = GraphGroupTree(layout_list, plot_dict)
    print gt
