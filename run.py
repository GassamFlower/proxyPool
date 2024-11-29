#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File_Name: run
"""
@Author: LYG
@Date: 2024/11/27
@Description: 
"""
from proxypool.storages.redis_client import RedisClient
from proxypool.crawlers.public.IP3366Crawler import IP3366Crawler


def main():
    redis_client = RedisClient()
    crawler = IP3366Crawler()
    for proxy in crawler.crawl():
        redis_client.add(proxy)


if __name__ == '__main__':
    main()
