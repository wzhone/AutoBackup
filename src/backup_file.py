from common import G
import os
from os.path import join,exists,dirname
from shutil import copy2
from common import removeFile

'''

因为git的特殊性，被删除的文件就算是删了，也不会

'''

# 在路径最后增加一个斜线
def addSlash(path):
    if path[len(path)-1] != '/':
        return "%s/" % path
    else:
        return path

# 获取一个目录相对父目录的关系
def getRelativePath(path,root):
    slen = len(path)
    if root[:slen] != path:
        G.log.error("系统错误： 目录[%s] [%s] 关系错误" 
            % (path,root))
        return
    return root[slen:]

def copy_file(source,dest):
    dirn = dirname(dest)
    if not exists(dirn):
        os.makedirs(dirn)
    copy2(source,dest)


# 备份文件
def backup(task):
    source = addSlash(task.source)
    dest = addSlash(task.path)

    ignore = task.ignore

    dealpath = []
    allfile = 0
    copyf = 0
    for root, dirs, files in os.walk(source):
        for file in files:
            if file in ignore: continue
            sourcefile =  join(root,file)
            destfile =  join(dest,getRelativePath(source,root),file)
            allfile += 1
            if os.path.exists(destfile):
                if os.path.isdir(destfile):
                    # 用户可能将之前的文件删了然后加上了同名文件夹
                    copy_file(sourcefile,destfile)
                else:
                    # 比对时间辍
                    stime = os.stat(sourcefile).st_mtime
                    dtime = os.stat(destfile).st_mtime
                    if stime > dtime:
                        # 替换文件
                        copy2(sourcefile,destfile)
                        copyf += 1
            else:
                # 创建这个文件并复制过去
                copy_file(sourcefile,destfile)
                copyf += 1
            
            dealpath.append(destfile)
    
    delfile = 0
    # 删除源文件库已经没有的文件
    for root, dirs, files in os.walk(dest):
        for file in files:
            path = join(root,file)
            if path not in dealpath:
                removeFile(path)
                delfile += 1

    msg = "共有[%s]个文件 更新[%s] 删除[%s]"
    G.log.debug(msg % (allfile,copyf,delfile))
    return True