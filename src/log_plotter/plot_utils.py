#!/usr/bin/env python

import time
import csv
import os
import re
import fnmatch
import numpy
import functools

def my_time(func):
    """
    Decorator for time measurement
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        print("start : " + func.__name__)
        result = func(*args, **kwargs)
        print('{0:>10} : {1:3.3f} [s]'.format(func.__name__,
                                              time.time() - start))
        return result
    return wrapper

# seems that we should declare global function for multiprocess
def readOneTopic(fname):
    data = []
    try:
        with open(fname, 'r') as f:
            reader = csv.reader(f, delimiter=' ')
            for row in reader:
                dl = filter(lambda x: x != '', row)
                data.append([float(x) for x in dl])
    except Exception as e:
        print('[readOneTopic] error occured while reading {}'.format(fname))
        print('[readOneTopic] {} may not exist.'.format(os.path.basename(fname)))
        print('[readOneTopic] skip data and return None data')
        return None
    return numpy.array(data)

def findFile(pattern, path):
    """
    Return file list matching specific substring
    """
    result = []
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(os.path.join(root, name))
    return result

def replaceRHString(fname_list):
    """
    Replace RobotHardware0 to each simulation-specific string
    """
    log_dir = os.path.dirname(os.path.abspath(fname_list[0]))
    base_name = os.path.splitext(os.path.basename(fname_list[0]))[0]
    # choreonoid
    if findFile(base_name + '.RobotHardware_choreonoid0_*', log_dir):
        fname_list = [fname.replace('.RobotHardware0_', '.RobotHardware_choreonoid0_') for fname in fname_list]
        return fname_list
    # hrpsys simulator
    elif findFile(base_name + '.*(Robot)0_*', log_dir):
        # pick up robot name (.<ROBOT_NAME>(Robot)0_)
        rep = re.sub(findFile(base_name + '.*(Robot)0_*', log_dir)[0].split('(Robot)0_')[1], '',
                     os.path.splitext(findFile(base_name + '.*(Robot)0_*', log_dir)[0])[1])
        fname_list = [fname.replace('.RobotHardware0_', rep) for fname in fname_list]
        return fname_list
    else:
        return fname_list
