from common import G
import pymysql
import re
import os




AllTableData = None

# 获取所有表的信息
def getAllDBTables(db_name):
    try:
        global AllTableData
        if not AllTableData is None:
            return AllTableData[db_name]

        host = G.database_info["host"]
        user = G.database_info["user"]
        password = G.database_info["password"]
        port = int(G.database_info["port"])

        conn = pymysql.connect(
            host=host,
            user=user,
            password=password,
            port=port,
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

        AllTableData = tablesdata
        return tablesdata[db_name]
    except pymysql.err.OperationalError as e:
        G.log.warn("数据库[%s]发生错误: [%s]" % (db_name,e))
        return None
    except KeyError:
        G.log.warn("数据库[%s]不存在" % db_name)
        return None


# 根据通配符去匹配表名
def matchWildcard(wild,tables):
    wild = re.escape(wild)
    wild = wild.replace("\\*",".*")
    wild = wild.replace("\\?",".")
    ret = []
    for i in tables:
        if re.match(wild,i) != None:
            ret.append(i)
    return ret    

# 根据 所有表名单 和 匹配名单 计算匹配的表
def matchTable(alltables,tables,dbname):
    if "*" in tables: return alltables

    target = []
    for table in tables:
        hasStar = ((table.find('*') != -1) or (table.find('?') != -1))

        if hasStar:
            target += matchWildcard(table,alltables)
        else:
            if table not in alltables:
                G.log.warn("数据表[%s] 不在数据库[%s]中" % (table,dbname))
                continue
            target.append(table)
    
    return target

# 获取mysqldump命令前缀
def getMysqlDumpPrefix(dbname):
    
    return 


# 备份一个数据表
def backupOneTable(dbname,tablename,path):
    prefix = getMysqlDumpPrefix(dbname)

    command = 'mysqldump -h%s -u%s -p%s -P%s %s --complete-insert --skip-extended-insert'
    prefix = command % (
        G.database_info["host"],
        G.database_info["user"],
        G.database_info["password"],
        G.database_info["port"],
        dbname
    )

    file = os.path.join(path,"%s.sql" % tablename)
    cmd = "%s %s > %s" % (prefix,tablename,file)
    return (os.system(cmd) == 0)

# 备份数据库
def backup(task):
    dbname = task.dbname
    tables = task.tables 
    ignore = task.ignore_tables
    path   = task.path

    # 准备要备份的表
    alltables = getAllDBTables(dbname)
    if alltables is None:
        return False
    elif len(alltables) == 0:
        G.log.warn("数据库[%s]为空" % dbname)
        return False

    # 筛选目标表
    target_table = matchTable(alltables,tables,dbname)

    # 去除忽略的表
    for i in ignore:
        if i in target_table:
            target_table.remove(i)

    if len(target_table) == 0:
        G.log.warn("数据库 [%s]备份任务： 需要备份的数据表为空" % dbname)
        return False

    G.log.message("备份数据库 [%s]" % dbname)
    G.log.debug("备份数据表 [%s]" % ','.join(target_table))


    # 逐个生成备份文件
    for table in target_table:
        r = backupOneTable(dbname,table,path)
        if not r:
            G.log.warn("数据库[%s]的数据表[%s]备份失败" % (table,dbname))
    
    return True