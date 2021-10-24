#!/bin/bash

# 编译备份系统
echo "Compile the python project"
cd ../src/
rm -rf ./dist
pyinstaller -F backup.py
ret=$?
cd ../test
cp ../src/dist/backup ./

if [[ $ret -ne 0 ]]; then 
    echo "ERROR: Compile error";
    exit 1
fi

echo "--------------------"
./backup -v

# 构建测试环境
mysql -uroot -proot < ./bundle/clean.sql
rm -rf /tmp/bundle

cp -r ./bundle /tmp/bundle
mysql -uroot -proot < ./bundle/bundle.sql

echo "--------------------"

# 第一次执行备份计划
./backup clean -c config.json -n -d
if [[ $ret -ne 0 ]]; then 
    echo "ERROR: The first backup failed ";
    exit 2
fi

mv ./data/.git ./git.tmp
tar --mtime='UTC 2021-01-01' -cf data.1.tar ./data/
mv ./git.tmp ./data/.git
sha_1=`sha1sum data.1.tar | awk '{print $1}'`
rm -f data.1.tar


# 第二次执行备份计划
./backup backup -c config.json -n -d
if [[ $ret -ne 0 ]]; then 
    echo "ERROR: The second backup failed";
    exit 3
fi
mv ./data/.git ./git.tmp
tar --mtime='UTC 2021-01-01' -cf data.2.tar ./data/
mv ./git.tmp ./data/.git
sha_2=`sha1sum data.2.tar | awk '{print $1}' ` 
rm -f data.2.tar
echo "--------------------"

# 清理环境
mysql -uroot -proot < ./bundle/clean.sql
rm -rf /tmp/bundle
rm -rf ./data

#echo $sha_1
#echo $sha_2


res="843ebeb7d59ba16706e322d056b027b049aca6b6"

if [[ "$sha_1" != "$res" ]]; then
	echo "第一次校验失败"
	exit 4
fi
if [[ "$sha_2" != "$res" ]]; then
	echo "第二次校验失败"
	exit 4
fi

echo "Test Pass"
exit 0
