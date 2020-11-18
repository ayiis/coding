#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    Build the .jade file into html recursively.
    https://github.com/pugjs/pug
    https://github.com/syrusakbary/pyjade

    1. 将 jade 转为 html
    2. 替换 html 里面的 <jade:*>*</jade:*> 标签
"""
import os
import re
import codecs
from pathlib import Path
from pyjade.ext.html import Compiler
from pyjade.utils import process


class JadeWork:
    """
        1. 将 jade 转为 html 缓存到内存 _mem 中
        2. 解析所有 _mem 里的 <jade:*>*</jade:*> 标签
        3. 保存结果到文件
    """
    _mem = {}
    _reading = set({})
    _read = set({})
    _method = {"include"}   # 所有支持的 jade 语法标签，例如 jade:include header.jade

    @classmethod
    def _convert_jade(cls, jade_file):
        """
            读取 jade 文件并转化为 html 标签形式
        """
        with codecs.open(jade_file, "r", encoding="utf-8") as rf:
            return process(rf.read(), compiler=Compiler, staticAttrs=True, extension=None)

    @classmethod
    def _convert_dir_jade(cls, source_path, target_path):

        if not Path(target_path).exists():
            os.makedirs(target_path)

        for path in Path(source_path).glob("*"):

            source_file = os.path.join(source_path, path.name)

            if path.is_dir():
                cls._convert_dir_jade(source_file, "%s/%s" % (target_path, path.name))
            elif path.is_file():
                if path.name[-5:] == ".jade" and len(path.name) > 5:
                    cls._mem[source_file] = cls._convert_jade(source_file)
                else:
                    print("Skip file in `_convert_dir_jade`: %s" % (source_file), flush=True)
            else:
                print("! Interesting path: %s" % path.name, flush=True)

    @classmethod
    def convert_dir_jade(cls, source_path, target_path):
        """
            解析 jade 并将结果缓存到 _mem 里
        """
        if not Path(source_path).is_dir():
            raise Exception("%s must be a dir!" % source_path)

        if not Path(target_path).exists():
            os.makedirs(target_path)
        elif not Path(target_path).is_dir():
            raise Exception("%s must be a dir!" % target_path)

        cls._convert_dir_jade(source_path, target_path)

    @classmethod
    def include(cls, source_file, source_path, target_path, text):
        """
            jade:inclde 语法解析，例如
            jade:inclde header.jade
        """
        target_path_dir = os.path.dirname(os.path.abspath(source_file))
        include_file = os.path.join(target_path_dir, text)
        return cls._format_mem(include_file, source_path, target_path, source_file)

    @classmethod
    def handle_jade(cls, source_file, source_path, target_path):
        """
            jade:* 语法解析，对应类内的方法
        """
        res = []
        regstr = "|".join([r"\<jade\:(%s)\>(.*)\</jade\:%s\>" % (x, x) for x in cls._method])
        for line in cls._mem[source_file].splitlines():
            reg_res = re.match(".*%s.*" % regstr, line)
            if reg_res:
                method, text = reg_res.groups()
                jade_res = getattr(cls, method)(source_file, source_path, target_path, text)
                res.append(jade_res)
            else:
                res.append(line)

        return "\r\n".join(res)

    @classmethod
    def _format_mem(cls, source_file, source_path, target_path, from_file=None):

        # 如果当前文件还没完成上一次解析，说明存在循环引用
        if source_file in cls._reading:
            raise Exception("Cyclic dependence found in %s" % (source_file))

        # 如果缓存 _mem 里不存在当前文件（上一步解析 jade 后会写入 _mem ），则说明当前文件不存在
        if source_file not in cls._mem:
            raise Exception("%s not found when formatting %s" % (source_file, from_file))

        # 如果文件未解析，进行解析
        if source_file not in cls._read:

            cls._reading.add(source_file)
            cls._mem[source_file] = cls.handle_jade(source_file, source_path, target_path)
            cls._reading.remove(source_file)
            cls._read.add(source_file)

        return cls._mem[source_file]

    @classmethod
    def format_mem(cls, source_path, target_path):
        """
            解析 _mem 里的 jade:* 标签
        """
        for source_file in cls._mem:
            cls._format_mem(source_file, source_path, target_path)

    @classmethod
    def write_result(cls, source_path, target_path):
        """
            将最终结果写入目标路径，同时去掉 .jade 的文件后缀名
        """
        for source_file in cls._mem:
            target_file = "%s%s" % (target_path, source_file[len(source_path):-5])
            with codecs.open(target_file, "w", encoding="utf-8") as wf:
                wf.write(cls._mem[source_file])

    @classmethod
    def build(cls, source_path, target_path):
        """
            1. 解析 jade 并将结果缓存到 _mem 里
            2. 解析 _mem 里的 jade:* 标签
            3. 将最终结果写入目标路径，同时去掉 .jade 的文件后缀名
        """
        source_path = os.path.abspath(source_path)
        target_path = os.path.abspath(target_path)

        # 清理
        cls._mem = {}
        cls._reading = set({})
        cls._read = set({})

        cls.convert_dir_jade(source_path, target_path)
        cls.format_mem(source_path, target_path)
        cls.write_result(source_path, target_path)

        return cls._mem


if __name__ == "__main__":
    JadeWork.build("src_jade", "src")
