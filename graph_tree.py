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
                    if not issubclass(type(tmp), list):
                        tmp_list.append([tmp])
                    else:
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
        member = [GraphGroup(self, row) for row,_ in enumerate(self.layout_list)]
        MultiArray.__init__(self, member)

    def complement_layout_list():
        pass

    def complement_plot_dict():
        pass

class GraphGroup(MultiArray, PlotDictInterface):
    '''
    graphs in line
    '''
    def __init__(self, parent, row):
        '''
        parent_tree: parent tree
        layout: one member from layout.yaml
        this class is list of graphs belonging to the same graph group
        '''
        self.parent = parent
        self.row = row
        self.layout = self.parent.layout_list[row]
        self.name = self.layout['group']
        PlotDictInterface.__init__(self)
        col_max_len = max([len(item) for item in self.layout['index']])
        members = [GraphInfo(self, index) for index in range(col_max_len)]
        MultiArray.__init__(self, members)

class GraphInfo(MultiArray, PlotDictInterface):
    '''
    each graph
    '''
    def __init__(self, parent, col):
        self.parent = parent
        self.col = col
        self.layout = self.parent.layout.copy()
        self.layout['index'] = [item[self.col] for item in self.parent.layout['index']]
        self.name = str('{}[{}]'.format(self.parent.name, self.layout['index'][0]))
        PlotDictInterface.__init__(self)
        members = [LegendInfo(self, legend_idx) for legend_idx, _ in enumerate(self.layout['index'])]
        MultiArray.__init__(self, members)

class LegendInfo(PlotDictInterface):
    '''
    each legend in graph
    '''
    def __init__(self, parent, index):
        self.parent = parent
        self.index = index
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
