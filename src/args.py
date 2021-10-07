import os
import json
import argparse
from common import G
from common import getAttr

class Args:
    def __init__(self) -> None:
        parser = argparse.ArgumentParser(
            description='自动备份 V2.0.1 Beta',
            epilog='不做完整性测试的备份不如不备份')
        parser.add_argument('mode',metavar='mode',help = "需要指定模式 backup/clean/status")
        parser.add_argument('-c','--config',dest = "config",help = "配置文件")
        parser.add_argument('-d','--debug',dest = "debug",help = "调试模式",action="store_true")
        parser.add_argument('-f','--force',dest = "force",help = "强制Commit",action="store_true")
        args = parser.parse_args()

        self.parser = parser
        self.args = args


        G.DEBUG = getAttr(args,"debug",False)
        G.log.debug("启用调试信息输出")

        G.FORCECOMMIT = getAttr(args,"force",False)
        if G.FORCECOMMIT:
            G.log.debug("开启强制Commit模式")


    def get(self,name,default):
        return getAttr(self.args,name,default)

    def __getattr__(self, name):
        return self.get(name,None)

