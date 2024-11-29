#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File_Name: IP3366Crawler
"""
@Author: LYG
@Date: 2024/11/27
@Description: 
"""
from bs4 import BeautifulSoup
from proxypool.schemas.proxy import Proxy
from proxypool.crawlers.base import BaseCrawler

BASE_URL = 'http://www.ip3366.net/free/?stype=1&page={page}'


class IP3366Crawler(BaseCrawler):
    urls = [BASE_URL.format(page=page) for page in range(1, 8)]
    """
    www.ip3366.net/free  云代理-免费IP
    """
    def parse(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        content = soup.find_all('table', {'class': 'table table-bordered table-striped'})
        tr_content = content[0].find_all('tr')
        for td in tr_content:
            if td.find_all('td'):
                proxy = Proxy(td.find_all('td')[0].text, int(td.find_all('td')[1].text))
                yield proxy


if __name__ == '__main__':
    crawler = IP3366Crawler()
    for proxy in crawler.crawl():
        print(f"当前IP：{proxy}")

