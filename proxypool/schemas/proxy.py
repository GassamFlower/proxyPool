#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File_Name: proxy
"""
@Author: LYG
@Date: 2024/11/26
@Description: 用于表示代理服务器的基本信息
"""


class Proxy(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def __str__(self):
        return f"{self.host}:{self.port}"

    def string(self):
        return self.__str__()


if __name__ == '__main__':
    proxy = Proxy('192.168.127.12', 8080)
    print('proxy', proxy)
    print('proxy', proxy.string())
