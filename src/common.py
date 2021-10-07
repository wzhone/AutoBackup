import os
import sys
import shutil
import time
from os.path import join


# 获取参数
def getAttr(data,key,default):
    r = getattr(data,key)
    if r is None:
        return default
    else:
        return r



class SingleGlobal():
    def __init__(self):
        path = os.path.dirname(os.path.realpath(sys.argv[0]))
        data = {
            "DEBUG" : False,
            "isFirst" : False,
            "FORCECOMMIT" : False,
            "NOLOG" : False,
            "filepath" : path
        }
        self.__dict__["data"] = data


    def __getattr__(self, name):
        data = self.data

        r = None
        if name in data:
            r = data[name]
        
        # print(name , r)
        if r is None:
            raise Exception("Global variable [%s] is not defined" % name)
        else:
            return r

    def __setattr__(self, name, value):
        self.data[name] = value


G = SingleGlobal()


# 部署项目
def deploy():
    pass

# 执行命令
def execCommand(command,path):
    cmd = "cd %s && %s"
    cmd = cmd % (path,command)
    return os.system(cmd)





# 目录关系
def isParent(son,parent):
    son = os.path.normpath(os.path.abspath(son)).split('/')
    parent = os.path.normpath(os.path.abspath(parent)).split('/')
    if son[0] == '':
        del son[0]
    if parent[0] == '':
        del parent[0]

    if len(son) < len(parent):
        return False

    for i in range(0,len(parent)):
        if son[i] != parent[i]:
            return False
    return True

# 删除文件或文件夹
def removeFile(path):
    path = os.path.abspath(path)

    if not os.path.exists(path):
        G.log.debug("删除不存在的文件 %s" % path)
        return

    if not isParent(path,G.workpath):
        G.log.error("删除的目录在GIT目录之外：%s" % path)

    if path == "/":
        G.log.error("删除的目录为根目录！！")

    parentpath = os.path.dirname(path)

    if not os.access(parentpath,os.W_OK):
        G.log.error("没有删除这个文件的权限 (%s)" % path)

    if os.path.isdir(path):
        shutil.rmtree(path)
    else:
        os.unlink(path)




# 带密码压缩文件
# def compress(sourcefile,destfile,password = ""):
#     with py7zr.SevenZipFile(destfile, 'w') as archive:
#         archive.writeall(sourcefile)

# 带密码解压文件
# def decompress(sourcefile,destfile,password = ""):
#     archive = py7zr.SevenZipFile(sourcefile, mode='r',password=password)
#     archive.extractall(path=destfile)
#     archive.close()



# 获取工作目录的大小
def getWorkPathSize():
    size = 0
    for path, dirs, files in os.walk(G.workpath):
        for f in files:
            fp = os.path.join(path, f)
            size += os.path.getsize(fp)
    return  round(size / 1024 / 1024 ,2)


def friendlyTime(t):
    now = int(time.time())
    value = now - t
    if value < 60:
        return "%d秒前" % value
    elif value < 3600:
        return "%d分钟前" % int(value / 60)
    elif value < 86400:
        m = int(value % 3600 / 60)
        h = int(value / 3600)
        return "%d小时 %d分前" % (h,m)
    else:
        d = int(value / 86400)
        h = int(value % 86400 / 3600)
        return "%d天 %d小时前" % (d,h)