#!/usr/bin/python3
'''
    Backup & Deploy System
    Author: wzh
    Date: 2021.9.15
'''

import os
import sys
import time
from os.path import join

from git import exc
sys.dont_write_bytecode = True



# 全局变量初始化区
_DEBUG = False
_FORCECOMMIT = False
_NOLOG = False

log = None
config = None

args = []
repo = None # 仓库句柄

workpath = None  # git目录
filepath = sys.path[0] # 本文件目录

isFirst = False
tableData = None

# 可能需要安装的包
try:
    
    import shutil
    import argparse
    import py7zr
    from git import Repo
    import git
    from jsoncomment import JsonComment
    from json.decoder import JSONDecodeError
    import pymysql

except ModuleNotFoundError as e:
    log.error("module not found (%s)" % e)

'''
    工具函数
'''

# 带密码压缩文件
# def compress(sourcefile,destfile,password = ""):
#     with py7zr.SevenZipFile(destfile, 'w') as archive:
#         archive.writeall(sourcefile)

# 带密码解压文件
# def decompress(sourcefile,destfile,password = ""):
#     archive = py7zr.SevenZipFile(sourcefile, mode='r',password=password)
#     archive.extractall(path=destfile)
#     archive.close()

# 获取参数
def getAttr(data,key,default):
    r = getattr(data,key)
    if r is None:
        return default
    else:
        return r

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
def removeFile(path,force = False):
    path = os.path.abspath(path)

    if not os.path.exists(path):
        return

    if not isParent(path,workpath):
        log.error("删除的目录在GIT目录之外：%s" % path)

    if path == "/":
        log.error("删除的目录为根目录！！")

    parentpath = os.path.dirname(path)

    if not os.access(parentpath,os.W_OK):
        log.error("没有删除这个文件的权限 (%s)" % path)

    if os.path.isdir(path):
        shutil.rmtree(path)
    else:
        os.unlink(path)

# 检查有没有大于100MB的文件 (返回值，（大小(MB)，路径）)
fileOver100MB = []
def checkFileSize():
    global fileOver100MB
    max = (0,"")
    for root,dirs,files in os.walk(workpath):
        for file in files:
            path = os.path.join(root,file)
            size = os.path.getsize(path)
            if size > 104857600:
                fileOver100MB.append(path)
            if size > max[0]:
                max = (size,path)

    s =  round(max[0] / 1024 / 1024,2)
    max = ( s, max[1]) 
    return max

# 删除大于100MB的文件
def deleteOver100MB():
    global fileOver100MB
    for i in fileOver100MB:
        log.warning("因为过大而删除文件：%s" % i)
        removeFile(i)
    fileOver100MB = []

'''
    日志工具类
'''
class Logger:
    def now(self):
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) 

    def __init__(self,file):
        try:
            self.f_handler = open(file,mode='a+')
            self.wirtable = True
        except PermissionError as e:
            self.wirtable = False
            print("The log file has no permissions : %s" % e)

    def __del__(self):
        if self.wirtable:
            self.f_handler.close()

    def error(self,str):
        self.__setBrush("1;31")
        self.__log("ERROR",str)
        self.__resetBrush()
        raise SystemExit(str)
        
    def warning(self,str):
        self.__setBrush("1;33")
        self.__log("WARNING",str)
        self.__resetBrush()

    def message(self,str):
        self.__setBrush("1;32")
        self.__log("MSG",str)
        self.__resetBrush()

    # 只有开启DEBUG开关，才会输出到屏幕和日志里
    def debug(self,str):
        if (_DEBUG):
            self.__log("DEBUG",str)

    def __log(self,t,s):
        str = "%s [%s] %s" %(self.now(),t,s)
        if not _NOLOG:
            print(str)
        self.__write(str)

    def __write(self,str):
        str = "%s\n" % str
        if self.wirtable:
            self.f_handler.write(str)

    def __resetBrush(self):
        print("\033[0m",end="")

    def __setBrush(self,str):
        print("\033[%sm" % str , end="")


'''
    配置文件读取工具类
'''
class Config:
    def __init__(self,file,isList = False):

        if isList:
            self.data = file
        else:
        # 读取配置文件
            try:
                log.debug("读取配置文件 %s" % file)
                with open(file,"r") as f:
                    content = f.read()
                    json = JsonComment()
                    self.data = json.loads(content)
            except JSONDecodeError as e:
                log.error("配置文件解析错误： %s" % e)
                return False
            except FileNotFoundError as e:
                log.error("配置文件不存在： %s" % e)
                return False

    def get(self,query):
        list = query.split('.')
        data = self.data
        for i in list:
            if i not in data:
                log.error("配置文件错误，缺少 %s" % query)
                raise SystemExit()
            else:
                data = data[i]
        return data

    def query(self,query,default):
        warn = "配置文件缺少 (%s)，使用缺省值 (%s)" % (query,default)
        list = query.split('.')
        data = self.data
        for i in list:
            if i not in data:
                if (_DEBUG): # 因为参数可选，所以仅限DEBUG才输出
                    log.warning(warn)
                return default
            else:
                data = data[i]
        return data

#------------------------------------------------------------


# 获取文件锁
def lockFile():
    lock = join(filepath,"backup.lock")
    if os.path.exists(lock):
        with open(lock,"r") as f:
            c = f.read()
            log.error("其他程序正在运行 PID: %s" % c)
            return False
    else:
        with open(lock,"w") as f:
            c = f.write("%s" % os.getppid())
            return True

# 解锁文件锁
def unlockFile():
    lock = join(filepath,"backup.lock")
    removeFile(lock)

# 部署项目
def deploy():
    pass

# 执行命令
def execCommand(command,path):
    cmd = "cd %s && %s"
    cmd = cmd % (path,command)
    os.system(cmd)

# 创建.gitignore
def makeIgnore(path,list):
    with open(join(path,".gitignore"),"w+") as f:
        f.writelines(["%s\n" % i for i in list])

# 备份文件
def backupFile(data,path):
    makeIgnore(path,data.query("ignore",[]))

    source = data.get("source")
    if not os.path.exists(source):
        log.error("文件不存在 : %s" % source)

    if os.path.isdir(source):
        c = source[len(source)-1]
        if c=='/' or c=='\\':
            source = source[0:len(source)-1]
        name = os.path.basename(source) #目标文件夹的名字
        dpath = join(path,name)
        shutil.copytree(source,dpath)
    else:
        shutil.copy2(source,path)

    return True

# 获取所有表的信息
def getAllDBTables():
    global tableData

    if not tableData is None:
        return

    host = config.get("database.host")
    user = config.get("database.user")
    password = config.get("database.password")

    try:
        conn = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database="information_schema"
        )
        cursor = conn.cursor()
        sql = 'select TABLE_SCHEMA,TABLE_NAME  from TABLES'
        cursor.execute(sql)
        tables = cursor.fetchall()
        tablesdata = {}
        for table in tables:
            dbname = table[0]
            tbname = table[1]
            if dbname not in tablesdata:
                tablesdata[dbname]= []

            tablesdata[dbname].append(tbname)

        tableData = tablesdata
    except pymysql.err.OperationalError as e:
        log.error("数据库错误: %s" % e)

# 获取mysqldump命令前缀
def getMysqlDumpPrefix(dbname):
    command = 'mysqldump -h%s -u%s -p%s %s --complete-insert  --skip-extended-insert'
    return command%(
        config.get("database.host"),
        config.get("database.user"),
        config.get("database.password"),
        dbname
    )

# 备份一个表
def backupOneTable(dbname,tablename,path):
    prefix = getMysqlDumpPrefix(dbname)
    file = join(path,"%s.sql" % tablename)
    cmd = "%s %s > %s" % (prefix,tablename,file)
    os.system(cmd)

# 备份数据库
def backupDB(data,path):
    dbname = data.get("dbname") 
    tables = data.get("tables") 

    if data.query("whitelist",True):
        # 白名单
        log.debug("数据库 %s 以白名单进行备份" % dbname)

        for t in tables:
            backupOneTable(dbname,t,path)
    else:
        # 黑名单
        black = data.query("tables",[])

        log.debug("数据库 %s 以黑名单进行备份" % dbname)
        
        getAllDBTables()
        tables = [] # 只有白名单才需要表的列表
        try:
            tables = tableData[dbname]
        except KeyError:
            log.error("数据表 %s 不存在" % dbname )

        for t in tables:
            if t in black:
                continue
            backupOneTable(dbname,t,path)

# 处理每个任务项
def dealTask(name,data):
    # 创建任务目录
    taskpath = join(workpath,name)
    removeFile(taskpath)
    os.mkdir(taskpath)

    hook = data.query("hook","everytime")
    if hook == "once":
        if not isFirst:
            log.debug("任务 %s 因为 once ，未执行" % name)
            return
    elif hook == "everytime":
        pass
    else:
        log.error("不支持的运行频率 hook: %s" % (hook))
        
    
    beforHook = data.query("beforHook",[])
    afterHook = data.query("afterHook",[])

    # 判断备份类型
    handle = None
    typ = data.get("type")
    if typ == "file":
        handle = backupFile
    elif typ == "database":
        handle = backupDB
        afterHook.append("sed -i '$d' *.sql") # 删除最后一行
    else:
        log.error("不支持的备份类型 %s:%s" % (name,typ))

    for c in beforHook:
        execCommand(c,taskpath)

    r = handle(Config(data.get("data"),True),taskpath)
    if r == False:
        return

    for c in afterHook:
        execCommand(c,taskpath)

    
    # 压缩

# 获取工作目录的大小
def getWorkPathSize():
    size = 0
    for path, dirs, files in os.walk(workpath):
        for f in files:
            fp = os.path.join(path, f)
            size += os.path.getsize(fp)
    return  round(size / 1024 / 1024 ,2)

# 备份项目
def backup():
    global repo

    # 根据每个项目生成对应的文件夹
    tasks = config.get("tasks")
    for kv in tasks.items():
        log.debug("处理任务: %s" % kv[0])
        dealTask(kv[0],Config(kv[1],True))

    # 生成.gitignore
    makeIgnore(workpath,config.query("ignore",[]))

    # 检查文件大小
    size = checkFileSize()
    log.debug("最大文件大小： %sMB, 文件路径 %s" % (size[0],size[1]))
    if (size[0] >= 100):
        log.warning("文件 %s，超过100MB！" % size[1])
    elif size[0] > 50:
        log.warning("文件 %s，超过50MB" % size[1])
    
    # 删除过大的文件
    deleteOver100MB()

    # 添加并提交
    log.debug("添加增加的文件")
    repo.git.add("-A")
    if _FORCECOMMIT or repo.is_dirty():
        commit_info = "%s" % log.now()
        repo.git.commit("--allow-empty","-am","'%s'" % commit_info)
        log.debug("向远程推送数据")
        repo.git.push("-u","-f","origin","master")
    else:
        log.message("无数据更新")

# 打印信息
def status():
    global _NOLOG
    _NOLOG = True # status 不写入日志
    log.message("工作目录大小： %sMB" % getWorkPathSize())

# 初始化参数
def initArgs():
    global args
    global _DEBUG
    global _FORCECOMMIT

    parser = argparse.ArgumentParser(description='自动备份部署系统')
    parser.add_argument('mode',metavar='mode',help = "需要指定模式 deploy/backup")
    parser.add_argument('-c','--config',dest = "config",help = "配置文件")
    parser.add_argument('-d','--debug',dest = "debug",help = "调试模式",action="store_true")
    parser.add_argument('-f','--force',dest = "force",help = "强制Commit",action="store_true")

    args = parser.parse_args()


    _DEBUG = getAttr(args,"debug",False)
    log.debug("启用调试信息输出")

    _FORCECOMMIT = getAttr(args,"force",False)
    if _FORCECOMMIT:
        log.debug("开启强制Commit模式")


# 重建仓库
def rebuildRepository():
    global repo
    global isFirst
    removeFile(workpath)
    
    log.debug("重建仓库")
    repo = Repo.init(join(workpath, ''), bare=False)
    with repo.config_writer() as c:
        c.set_value("user","name",config.get("git.name"))
        c.set_value("user","email",config.get("git.email"))
        c.set_value("credential","helper","store")

    # 生成remote连接
    info = "%s:%s" % (config.get("git.name"),config.get("git.password"))
    addr = config.get("git.address")
    addr = addr.replace("https://","https://%s@" % info)
    log.debug("增加远程连接 %s" % config.get("git.address"))
    repo.git.remote("add","origin",addr)

    isFirst = True

# 初始化仓库，有则获取，没则新建
def initGitRepository():
    global repo
    # 判断目录是否存在，如果不存在就初始化仓库
    if not os.path.exists(join(workpath,".git")):
        rebuildRepository()
    else:
        repo = Repo(join(workpath, ''))

#------------------------------------------------------------


def main():
    global log
    global config
    global workpath

    # 初始化日志
    log = Logger("/tmp/backup.log")

    # 锁定文件
    # if lockFile():
    #     log.debug("备份程序开始 PID %s" % os.getppid())
    # else:
    #     return


    # 初始化参数
    initArgs()

    # 初始化配置文件
    try:
        # 获取配置文件目录
        path = getAttr(args,"config",join(filepath,"config.json"))
        path = os.path.abspath(path)
        
        # 解析配置文件
        config = Config(path)
        workpath = os.path.abspath(config.get("repository"))
    except:
        log.error("配置文件解析错误，任务结束")
        return


    # 初始化仓库
    initGitRepository()

    try:
        mode = args.mode
        log.debug("执行命令 %s" % ' '.join(sys.argv))
        if mode == "deploy":   # 执行部署操作
            deploy()
        elif mode == "backup": # 执行备份操作
            backup()
        elif mode == "status": # 显示仓库的信息
            status()
        elif mode == "clean":  # 清理仓库，并重建                                                                                                                                                                                                                                                                        
            rebuildRepository()
            backup()
        else:
            log.error("不支持的模式 (%s)" % mode)
    except SystemExit as e:
        pass
    except git.exc.GitCommandError as e:
        log.error("GIT命令执行出错! : %s" % e)
    finally:    
        # 结束任务
        log.debug("备份程序结束 PID %s" % os.getppid())
        unlockFile()


if __name__ == "__main__":
    main()