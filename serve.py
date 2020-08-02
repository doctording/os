#-*- coding:utf-8 -*-
import os
from sys import argv

def gitbook_operation():
    os.system("gitbook build ./docs")
    os.system('gitbook serve ./docs')

if __name__ == '__main__':
    gitbook_operation()