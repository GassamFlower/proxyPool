#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File_Name: test_ip
"""
@Author: LYG
@Date: 2024/11/27
@Description: 检测模块
"""
import asyncio
import aiohttp
import logging
from proxypool.schemas.proxy import Proxy
from proxypool.setting.log_output import set_logger
from proxypool.storages.redis_client import RedisClient
logger_info = set_logger(log_name='TestLogger', name='info_test', log_file="info_test.log", level=logging.INFO)


class Tester(object):
    def __init__(self):
        self.redis = RedisClient()
        self.loop = asyncio.get_event_loop()

    async def tests(self, proxy: Proxy):
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
            try:
                logger_info.info(f"开始检测IP性能，当前IP：http://{proxy.string()}")
                async with session.get(url='https://www.httpbin.org/get', proxy=f'http://{proxy.string()}', timeout=10,
                                       allow_redirects=False) as response:
                    logger_info.info(f"response.status:{response.status}")
                    if response.status == 200:
                        logger_info.info(f"当前设置：{proxy.string()}")
                        self.redis.max(proxy)    # 第一次能使用，直接为最大值
                    else:
                        logger_info.info(f"没有符合的IP")
                        self.redis.decrease(proxy)
            except Exception as e:
                logging.info(f"当前问题：{e}")
                self.redis.decrease(proxy)

    def run(self):
        count = self.redis.count()
        for i in range(0, count, 5):
            start, end = i, min(i+5, count)
            proxies = self.redis.batch(start, end)
            tasks = [self.tests(proxy) for proxy in proxies[1]]
            self.loop.run_until_complete(asyncio.gather(*tasks))



if __name__ == '__main__':
    tester = Tester()
    tester.run()
