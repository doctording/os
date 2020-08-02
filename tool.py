#-*- coding:utf-8 -*-
import os
from sys import argv

def git_operation(commit_description):
    '''
    git 命令行函数，将仓库提交
    
    ----------
    需要安装git命令行工具，并且添加到环境变量中
    '''
    os.system("gitbook build ./docs")
    os.system('ghp-import -p -m "Update gitbook" -r origin -b gh-pages ./docs/_book')
    os.system('git add --all')
    os.system('git commit -m "%s"' % commit_description)
    os.system('git push origin master')

if __name__ == '__main__':
    # 第一个命令行参数当错commits的内容
    commit_description = "updated"  
    if len(argv) == 2 :
        commit_description = argv[1]
    print commit_description
    # git 提交
    git_operation(commit_description)