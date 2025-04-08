#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys, os, re

try:
    from modules.debugLogger import DebugLogger
except:
    sys.path.append("../")
    from debugLogger import DebugLogger

__version__="1.0.1"


class PathProcessing:
    """ 这是一个处理路径相关的类"""
    def __init__(self, logger=None):
        self.skip_list = []
        self.logger = logger
        if not self.logger:
            self.logger = DebugLogger()

    def get_file_list(self, dir_path, lock_regular=".c"):
        """
            功能:
                    * 递归获取指定目录下指定类型的文件列表
            参数：
                    * str 文件目录路径 dir_path
                    * str 锁定文件的正则表达式 lock_regular
            返回值:
                    * list 文件列表 flist
        """
        flist = []
        if not os.path.exists(dir_path):
            self.logger.log(f"[PathProcessing]: 错误! {dir_path} 路径下, 指定 {lock_regular} 规则文件不存在", "Error")
            return flist
        else:
            if os.path.isfile(dir_path):
                if re.findall(lock_regular, dir_path, re.I) and not re.findall("\.swp$", dir_path):
                    flist.append(dir_path)
                    return flist
                else:
                    return flist
            else:
                for i in os.listdir(dir_path):
                    tmp_path = os.path.join(dir_path,i)
                    if os.path.isdir(tmp_path) and os.listdir(tmp_path):
                        flist.extend(self.get_file_list(tmp_path, lock_regular))
                    elif re.findall(lock_regular, tmp_path, re.I) and not re.findall("\.swp$", tmp_path):
                        flist.append(tmp_path)
                return flist

if __name__=="__main__":
    pass

