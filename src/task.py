import time
import os
from common import G,removeFile,execCommand


class Task:
    def __init__(self, name, config) -> None:
        self.config = config
        self.name = name
        self.path = os.path.join(G.workpath, name)

        # check directory
        if not os.path.exists(self.path):
            os.mkdir(self.path)

        # get commmand
        self.beforHook = self.config.query("beforHook",[])
        self.afterHook = self.config.query("afterHook",[])

        # test hook
        self.runable = True
        hook = config.query("hook", "everytime")
        if hook == "once":
            if not G.isFirst:
                self.runable = False
                G.log.message("跳过任务 [%s]， 因为 once " % self.name)
        elif hook == "everytime":
            pass
        else:
            G.log.warn("不支持的运行频率 hook: %s" % (hook))
            self.runable = False
            return

        # get type
        tasktype = config.get("type")
        if tasktype == "file":
            self.runfun = self._backupfile
        elif tasktype == "database":
            self.runfun = self._backupdb
            self.afterHook.insert(0,"sed -i '$d' *.sql") # 删除最后一行
        else:
            G.log.warn("不支持的类型 Task:[%s] Type:[%s]" % (name,tasktype))
            self.runable = False
            return


    def _exec(self,commands,path) -> bool:
        for cmd in commands:
            r = execCommand(cmd,path)
            if r != 0:
                self.runable = False
                msg = "运行命令失败 Task:[%s] Command:[%s]"
                G.log.warn(msg % (self.name,cmd))

    def before(self):
        if self.runable:
            self._exec(self.beforHook,self.path)

    def after(self):
        if self.runable:
            self._exec(self.afterHook,self.path)

    def run(self):
        if self.runable:
            self.runfun()

    def _backupdb(self) -> bool:
        
        # 删除历史数据
        # 因为数据库备份的特殊性，所以可以每次都把以前的数据删除
        removeFile(self.path)
        os.mkdir(self.path)

        
        import backup_db
        self.tables = self.config.get("data.tables")
        self.dbname = self.config.get("data.dbname")
        self.ignore_tables = self.config.query("data.ignore",[])
        ret = backup_db.backup(self)
        if not ret:
            G.log.warn("执行备份[%s]失败" % self.name)
            self.runable = False
        return ret


    def _backupfile(self) -> bool:
        import backup_file
        self.source = self.config.get("data.source")
        self.ignore = self.config.query("data.ignore",[])
        ret = backup_file.backup(self)
        if not ret:
            G.log.warn("执行备份[%s]失败" % self.name)
            self.runable = False
        return ret



# https://github.com/owner/repository/releases/latest/download/ASSET.ext
