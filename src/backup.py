#!/usr/bin/python3
import os
from re import I
import sys
import time
from os.path import join
from config import Config
from common import G,removeFile,friendlyTime,getWorkPathSize
from args import Args
from log import Logger
from task import Task

# 可能需要安装的包
try:
    
    import shutil
    import argparse
    #import py7zr
    from git import Repo
    import git
    import pymysql

except ModuleNotFoundError as e:
    G.log.error("module not found (%s)" % e)


# 获取所有文件的大小 (根据大小，由大到小排序)
def getAllFileSize():
    filessize = []
    for root,dirs,files in os.walk(G.workpath):
        for file in files:
            path = os.path.join(root,file)
            size = os.path.getsize(path)
            filessize.append([path,size,file])

    return sorted(filessize, key=lambda k: k[1],reverse=True)

# 筛选大于100MB的文件
def checkFileSize(files):
    over100MB = []
    for file in files:
        size = file[1]
        if size > 104857600:
            over100MB.append([file[0],size])
    return over100MB

# 删除大于100MB的文件
def deleteIllegalFile(files):
    for f in files:
        G.log.warn("因为过大而删除文件：%s" % f[0])
        removeFile(f[0])

# 创建.gitignore
def makeGlobalIgnore(list):
    path = join(G.workpath,".gitignore")
    with open(path,"w+") as f:
        f.writelines(["%s\n" % i for i in list])

#-------------------

repo = None
# 备份项目
def backup():
    global repo

    # 列出所有备份任务
    tasks = G.config.get("tasks")
    taskObjs = []


    # 生成Task类
    for kv in tasks.items():
        path = join(G.workpath,kv[0])
        taskObjs.append(
            Task(kv[0],Config(kv[1],True))
        )

    # 重新生成全局.gitignore
    makeGlobalIgnore(G.config.query("ignore",[]))


    # 执行备份
    for obj in taskObjs:
        G.log.message("执行备份任务 [%s]" % obj.name)
        obj.before()
        obj.run()
        obj.after()

    # 检查文件大小，避免推送失败
    filesize = getAllFileSize()
    r = checkFileSize(filesize)
    deleteIllegalFile(r)
    for i in filesize:
        size = i[1]
        if size > 94371840:
            G.log.warn("文件 %s，超过90MB" % i[0])


    # 添加并提交
    G.log.debug("添加增加的文件(git add -A)")
    repo.git.add("-A")
    if G.FORCECOMMIT or repo.is_dirty():
        commit_info = "%s" % G.log.now()
        repo.git.commit("--allow-empty","-am","%s" % commit_info)
        G.log.debug("向远程推送数据")
        repo.git.push("-u","-f","backup_origin","master")
    else:
        G.log.message("无数据更新")

# 打印信息
def status():
    G.NOLOG = True # status 不写入日志
    print("备份目录大小 %sMB" % getWorkPathSize())

    commits = []
    for c in repo.iter_commits():
        commits.append(c)

    if len(commits) == 0:
        print("警告：仓库无任何推送!!!")
        return

    date = commits[0].committed_date
    print("最后一次提交是 %s" % friendlyTime(date))

    # 检查远程分支推送情况
    # last = commits[0].hexsha
    head = repo.head.object.hexsha

    try:
        remote = repo.remote('backup_origin')
        path = remote.refs[0].abspath
        r_hex = ""

        with open(path, 'r') as f:
            r_hex = f.read().strip()
    except IndexError:
        print("还没有任何推送!!")
        return

    if head != r_hex:
        print("本地分支与远程分支不匹配，可能有没推送上去的commit!!")
        print("请带 -f 参数重新执行备份命令")
        print("Remote - %s" % r_hex)
        print("Local  - %s" % head)

# 重建仓库
def rebuildRepository():
    global repo
    removeFile(G.workpath)
    
    G.log.debug("重建仓库")
    repo = Repo.init(join(G.workpath, ''), bare=False)
    G.isFirst = True

# 设置仓库的推送信息
def initRepoInfo(repo):
    with repo.config_writer() as c:
        c.set_value("user","name",G.config.get("git.name"))
        c.set_value("user","email",G.config.get("git.email"))
        c.set_value("credential","helper","store")

    # 生成remote连接
    info = "%s:%s" % (G.config.get("git.name"),G.config.get("git.password"))
    addr = G.config.get("git.address")
    addr = addr.replace("https://","https://%s@" % info)
    # G.log.debug("增加远程连接 %s" % G.config.get("git.address"))

    # 检查推送连接是否存在
    hasRemote = False
    for r in repo.remotes:
        if r.name == "backup_origin":
            hasRemote = True
    if not hasRemote:
        repo.git.remote("add","backup_origin",addr)


# 初始化仓库，有则获取，没则新建

def initGitRepository():
    global repo
    # 判断目录是否存在，如果不存在就初始化仓库
    if not os.path.exists(join(G.workpath,".git")):
        rebuildRepository()
    else:
        repo = Repo(join(G.workpath, ''))
    
    initRepoInfo(repo)


# 获取文件锁
def lockFile():
    lock = join(G.filepath,"backup.lock")
    if os.path.exists(lock):
        with open(lock,"r") as f:
            c = f.read()
            return c
    else:
        with open(lock,"w") as f:
            c = f.write("%s" % os.getppid())
            return True


# 解锁文件锁
def unlockFile():
    lock = join(G.filepath,"backup.lock")
    os.unlink(lock)


def init():


    # 初始化命令行
    G.args = Args()

    # 初始化配置文件
    try:
        # 获取配置文件目录
        path = G.args.get("config",join(G.filepath,"config.json"))
        path = os.path.abspath(path)
        
        # 解析配置文件
        G.config = Config(path)
        G.workpath = os.path.abspath(G.config.get("repository"))
    except:
        G.log.error("配置文件解析错误，任务结束")
        return

    # 初始化仓库
    initGitRepository()

    # 初始化数据库连接信息
    G.database_info = {
        "user" : G.config.query("database.user","root"),
        "host": G.config.query("database.host","127.0.0.1"),
        "password": G.config.query("database.password",""),
        "port" : G.config.query("database.port",3306)
    }


def main():
    # 初始化日志
    G.log = Logger("/tmp/autobackup.log")


    # 锁定文件
    ret = lockFile()
    if ret is True:
        G.log.debug("备份程序开始 PID:[%s]" % os.getppid())
    else:
        G.log.error("其他程序正在运行 PID: %s" % ret)
        return

    try:                
        # 初始化
        init()

        mode = G.args.mode
        G.log.debug("执行命令 %s" % ' '.join(sys.argv))
        if mode == "backup": # 执行备份操作
            backup()
        elif mode == "status": # 显示仓库的信息
            status()
        elif mode == "clean":  # 清理仓库，并重建                                                                                                                                                                                                                                                                        
            rebuildRepository()
            initRepoInfo(repo)
            G.log.debug("目录清理完毕")
            backup()
        else:
            G.log.error("不支持的模式 (%s)" % mode)
        
        G.log.message("备份程序结束 PID:[%s]" % os.getppid())
    except SystemExit as e:
        pass
    except git.exc.GitCommandError as e:
        G.log.error("GIT命令执行出错! : %s" % e)
    finally:    
        unlockFile()


if __name__ == "__main__":
    main()
