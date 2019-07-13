# -*- coding: utf-8 -*-
import yaml
import re

class GraphLegendInfo(object):
    def __init__(self, layout_yaml, plot_yaml, i, j, k):
        '''
        :param list layout_yaml: list loaded from layout.yaml
        :param dict plot_yaml: dict loaded from plot.yaml
        :param int  i: ith group in layout_yaml
        :param int  j: jth column in layout_yaml
        :param int  k: kth legend in graph
        '''
        self.graph_title = list(layout_yaml.keys())[i]
        self.group_info = list(layout_yaml.values())[i]
        self.plot_dict = plot_yaml
        self.group_index = i
        self.graph_index = j
        self.legend_index = k

        # colect info from plot.yaml
        my_info = {}
        my_key = self.group_info['legends'][k]['key']
        my_info.update(plot_yaml[my_key])
        my_info.update(self.group_info['legends'][k])
        # colect info from layout.yaml
        my_info.setdefault('func', 'normal')
        my_info.setdefault('label', my_key)

        # remove other legend info
        my_info['id'] = my_info['id'][j]
        my_info['data'] = [d.copy() for d in my_info['data']]
        for d in my_info['data']:
            d['column'] = d['column'][my_info['id']]

        # check contents
        for info_name in ['key', 'data', 'id', 'func', 'label']:
            assert info_name in my_info
        self.info = my_info

def expand_str_to_list (input_str):
    parsed = re.match("([0-9]+)-([0-9]+)", input_str)
    if parsed:
        return range(int(parsed.group(1)),int(parsed.group(2))+1)
    else:
        return input_str

if __name__=='__main__':
    with open('config/robot/jaxon/test.yaml', mode='r') as plot_conf:
        plot_dict = yaml.load(plot_conf)
    with open('config/robot/jaxon/test-layout.yaml', mode='r') as layout_conf:
        layout_list = yaml.load(layout_conf)

    # expand [0-33] => [0,1,2,...,33]
    for leg_info in plot_dict.values():
        for log_info in leg_info['data']:
            if type(log_info['column'][0]) == str:
                log_info['column'] = expand_str_to_list(log_info['column'][0])
    for group in layout_list:
        for leg in group['legends']:
            if type(leg['id'][0]) == str:
                leg['id'] = expand_str_to_list(leg['id'][0])

    for i, group in enumerate(layout_list):
        for k, legend in enumerate(group['legends']):
            for j, legend_id in enumerate(legend['id']):
                # print('title= {}, column= {}, legend= {}'.format(group['title'], j, legend['key']))
                legend_info = GraphLegendInfo(layout_list, plot_dict, i, j, k)
                print(legend_info.info)
