from common import G
from jsoncomment import JsonComment
from json.decoder import JSONDecodeError
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
                G.log.debug("读取配置文件 %s" % file)
                with open(file,"r") as f:
                    content = f.read()
                    json = JsonComment()
                    self.data = json.loads(content)
            except JSONDecodeError as e:
                G.log.error("配置文件解析错误： %s" % e)
                return False
            except FileNotFoundError as e:
                G.log.error("配置文件不存在： %s" % e)
                return False

    def get(self,query):
        list = query.split('.')
        data = self.data
        for i in list:
            if i not in data:
                G.log.error("配置文件错误，缺少 %s" % query)
                raise SystemExit()
            else:
                data = data[i]
        return data

    def query(self,query,default):
        debugmsg = "配置文件缺少 (%s)，使用缺省值 (%s)" % (query,default)
        list = query.split('.')
        data = self.data
        for i in list:
            if i not in data:
                if (G.DEBUG): # 因为参数可选，所以仅限DEBUG才输出
                    G.log.debug(debugmsg)
                return default
            else:
                data = data[i]
        return data