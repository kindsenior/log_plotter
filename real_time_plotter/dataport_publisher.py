#!/usr/bin/env python
# -*-coding:utf-8-*-

import threading
import rtctree.tree
import rtshell
import rtshell.comp_mgmt
import rtshell.modmgr
# import path
import rtshell.port_types
# import rtshell


import rtshell.gen_comp
import OpenRTM_aist
import RTC

import rospy
from std_msgs.msg import Float32MultiArray
from hrpsys_ros_bridge.msg import RTC_TimedDoubleSeq
import sys
import yaml

yamlfile=sys.argv[1]
f=open(yamlfile)
convertRules=yaml.load(f)
f.close()

topicName=convertRules['topicName']
portName=convertRules['portName']
def generatePublisher():
    pkgName=convertRules['msgType'][0]
    msgName=convertRules['msgType'][1]
    __import__(pkgName+".msg._"+msgName)
    msgType=getattr(sys.modules[pkgName+'.msg._'+msgName],msgName)
    return rospy.Publisher(topicName, msgType, queue_size=1000)
def Data2Msg(data):
    pkgName=convertRules['msgType'][0]
    msgName=convertRules['msgType'][1]
    __import__(pkgName+".msg._"+msgName)
    msgType=getattr(sys.modules[pkgName+'.msg._'+msgName],msgName)
    msg=msgType()
    for rr in convertRules['rule']:
        exec rr
    return msg

# topicName='abc_q'
# portName='/localhost:15005/abc.rtc:q'
# def generatePublisher():
#     from hrpsys_ros_bridge.msg import RTC_TimedDoubleSeq
#     return rospy.Publisher(topicName, RTC_TimedDoubleSeq, queue_size=1000)
# def Data2Msg(data):
#     from hrpsys_ros_bridge.msg import RTC_TimedDoubleSeq
#     msg=RTC_TimedDoubleSeq()
#     msg.data=data.data
#     msg.tm=data.tm
#     return msg


class comp_func(rtshell.gen_comp.GenComp):
    def __init__(self, mgr, port_specs, *args, **kwargs):
        rtshell.gen_comp.GenComp.__init__(self, mgr, port_specs, *args, **kwargs)
        self.pub = generatePublisher()
    def _behv(self, ec_id):
        execed = 0
        for p in self._ports.values():
            if p.port.isNew():
                execed = 1
                p.read()
                def publish(data):
                    msg=Data2Msg(data)
                    self.pub.publish(msg)
                    return True
                publish (p.data)
        return RTC.RTC_OK, execed
# class
class getPortData():
    def __init__(self):
        pass
    def main(self):
        # mm=<rtshell.modmgr.ModuleMgr>
        mm = rtshell.modmgr.ModuleMgr(verbose=True, paths=[])
        mm.load_mods_and_poas([])

        # targets=[(['localhost:15005', 'abc.rtc'],'q',None,None,'localhost:15005/abc.rtc:q')]
        raw_paths=[portName]
        targets = rtshell.port_types.parse_targets(raw_paths)

        paths = [t[0] for t in targets]
        tree = rtctree.tree.RTCTree(paths=paths, filter=paths)

        port_specs = rtshell.port_types.make_port_specs(targets, mm, tree)
        rtshell.port_types.require_all_input(port_specs)


        event = threading.Event()
        # rtprint options
        rate=100
        hz=-1 #t
        comp_name, mgr = rtshell.comp_mgmt.make_comp('rtprint_reader', tree, comp_func, port_specs, event=event, rate=rate,max=hz)
        # make component
        comp = rtshell.comp_mgmt.find_comp_in_mgr(comp_name, mgr)
        # connect ports
        rtshell.comp_mgmt.connect(comp, port_specs, tree)
        # activate
        rtshell.comp_mgmt.activate(comp)
        try:
            while True:
                raw_input()
                # The manager will catch the Ctrl-C and shut down itself, so don't
                # disconnect/deactivate the component
        except KeyboardInterrupt:
            pass
        except EOFError:
            pass
        # # dis connect
        rtshell.comp_mgmt.disconnect(comp)
        # # deactivate
        rtshell.comp_mgmt.deactivate(comp)

        tree.give_away_orb()
        rtshell.comp_mgmt.shutdown(mgr)


if __name__=='__main__':
    g=getPortData()
    rospy.init_node('dataport_publisher', anonymous=True)
    g.main()
