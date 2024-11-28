#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File_Name: base
"""
@Author: LYG
@Date: 2024/11/27
@Description: 
"""
from retrying import retry, RetryError
from fake_headers import Headers
from proxypool.setting.log_output import set_logger
import requests
import logging
import time

logger_info = set_logger(log_name='CrawlLogger', name='info_crawl', log_file="info_crawl.log", level=logging.INFO)


class BaseCrawler(object):
    urls = []

    @retry(stop_max_attempt_number=3, retry_on_result=lambda x: x is None, wait_fixed=2000)  # 自动重试
    def fetch(self, url):
        try:
            headers = Headers(headers=True).generate()  # 随机生成headers
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                response.encoding = 'utf-8'
                return response.text
        except RetryError as e:
            logger_info.info(f"BaseCrawler_fetch_RetryError:{e}")

    def process(self, html, url):
        """
        解析html页面
        """
        for proxy in self.parse(html):  # self.parse(html) 假定在子类总实现
            logger_info.info(f"fetched proxy {proxy.string()} from {url}")
            yield proxy

    def crawl(self):
        """
        主要爬取方法-核心
        yield from其目的是：将子生成器的值逐一交付给调用者。
                          自动处理子生成器的return值，直接作为父生成器的结果。
        """
        try:
            for url in self.urls:
                html = self.fetch(url)
                if not html:
                    continue
                time.sleep(3)
                """yield from将self.process(html, url)的结果直接交付给调用者，而不需要显着地用for循环逐个yield
                使用yield from可以减少代码量，并让逻辑更清晰"""
                yield from self.process(html, url)
        except RetryError as ce:
            logger_info.info(f"BaseCrawler_crawl_RetryError:{ce}")
