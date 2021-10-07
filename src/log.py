import time
from common import G

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
        
    def warn(self,str):
        self.__setBrush("1;33")
        self.__log("warn",str)
        self.__resetBrush()

    def message(self,str):
        #self.__setBrush("1;32")
        self.__log("MSG",str)
        #self.__resetBrush()

    # 只有开启DEBUG开关，才会输出到屏幕和日志里
    def debug(self,str):
        if (G.DEBUG):
            self.__setBrush("1;34")
            self.__log("DEBUG",str)
            self.__resetBrush()

    def __log(self,t,s):
        str = "%s [%s] %s" %(self.now(),t,s)
        if not G.NOLOG:
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

