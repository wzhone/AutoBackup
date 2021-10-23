import time
from common import G

'''
    日志工具类
'''
class Logger:

    def push(self):
        #self.__log("┍-","","")
        self.height += 1
        

    def pop(self):
        self.height -= 1
        self.__log("┕--","","")


    def now(self):
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) 

    def __init__(self,file):
        try:
            self.f_handler = open(file,mode='a+')
            self.wirtable = True
            self.height = 0

        except PermissionError as e:
            self.wirtable = False
            print("The log file has no permissions : %s" % e)

    def __del__(self):
        if self.wirtable:
            self.f_handler.close()

    def error(self,str):
        self.__log("ERROR",str,"1;31")
        raise SystemExit(str)
        
    def warn(self,str):
        self.__log("warn",str,"1;33")

    def message(self,str):
        self.__log("MSG",str,"1;37")

    # 只有开启DEBUG开关，才会输出到屏幕和日志里
    def debug(self,str):
        if (G.DEBUG):
            self.__log("DEBUG",str,"1;34")


    def __log(self,type,msg,color):
        str = "%s%s%s %s[%s] %s%s" % ("%s",self.__getPrefix(),"%s","%s",type,msg,"%s")
        if msg == "":
            str = "%s%s  %s%s%s%s" % ("%s",self.__getPrefix(),type,"%s","%s","%s")

        print_s = str % (self.getColor("1;32"),"\033[0m",self.getColor(color),"\033[0m")

        if not G.NOLOG:
            print(print_s)
            self.__write(str % ("","","",""))

    def __write(self,str):
        str = "%s\n" % str
        if self.wirtable:
            self.f_handler.write(str)

    def __getPrefix(self):
        str = ""
        for i in range(0,self.height):
            str += "  |"
        return str

    def getColor(self,str):
        return "\033[%sm" % str