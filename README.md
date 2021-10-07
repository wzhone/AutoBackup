# 自动备份！

`v1` 版于初版本

`v2` 初版于 `2021.9.20` 完成

`v2.0.1 Alpha`  `2021.10.7`

**要注意测试备份有效性测试！**



### 依赖包

```bash
pip3 install argparse
pip3 install pymysql
pip3 install JsonComment
pip3 install gitpython
```

### 打包方式

```
git clone https://github.com/wzhone/AutoBackup.git
cd AutoBackup/src
pyinstaller -F backup.py
cd dist
./backup -v
```

### 支持的平台

当前仅支持`Linux`
