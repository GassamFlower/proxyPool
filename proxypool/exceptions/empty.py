#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File_Name: empty
"""
@Author: LYG
@Date: 2024/11/26
@Description: 
"""


class PoolEmptyException(Exception):
    def __str__(self):
        """
       proxypool is used out
       :return:
       """
        return repr('no proxy in proxypool')