#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File_Name: redis_setting
"""
@Author: LYG
@Date: 2024/11/26
@Description: redis数据连接配置
"""
import redis
import logging
from proxypool.schemas.proxy import Proxy
from proxypool.exceptions.empty import PoolEmptyException
from proxypool.setting.log_output import set_logger
from random import choice

logger_info = set_logger(log_name='RedisLogger', name='info_redis_cl', log_file="info_redis_cl.log", level=logging.INFO)
PROXY_SCORE_MAX = 100
PROXY_SCORE_MIN = 0
PROXY_SCORE_INIT = 10
REDIS_KEY = 'PROXYPOOL_REDIS_KEY'


class RedisClient(object):
    def __init__(self):
        self.conn = None   # 连接情况
        self._connect()

    def _connect(self):
        """connect to redis server"""
        try:
            self.conn = redis.Redis(
                host='127.0.0.1', port=6379, password='redis@123', db=0,
                decode_responses=True)  # decode_responses=True,自动解码字节到字符串
            # test the connection
            self.conn.ping()
            logger_info.info(f'Connected to Redis......')
        except Exception as e:
            logger_info.info(f"Failed to connect to Redis:{e}")

    def add(self, proxy: Proxy, score=PROXY_SCORE_INIT, redis_key=REDIS_KEY):
        """
        向数据库中添加代理并设置分数，默认的分数是PROXY_SCORE_INIT
        :param redis_key:
        :param score: int score
        :param proxy: proxy, ip:port,like 8.8.8.8:88
        :return: result
        """
        try:
            logger_info.info(f"add data:{proxy.string():{score}}")
            return self.conn.zadd(redis_key, {proxy.string(): score})
        except Exception as e:
            print(f"Error setting key {redis_key}: {e}")
            return False

    def get_random(self, redis_key=REDIS_KEY, proxy_score_min=PROXY_SCORE_MIN, proxy_score_max=PROXY_SCORE_MAX):
        """
        首先获取100分的代理，然后随机选择一个返回。如果不存在100分的代理，则此方法按照排名来获取，选取前100名
        :param redis_key:
        :param proxy_score_min: 0
        :param proxy_score_max: 100
        :return: proxy
        """
        logger_info.info(f"get_random choice......")
        proxies = self.conn.zrangebyscore(redis_key, proxy_score_max, proxy_score_min, withscores=True)
        if len(proxies):
            return choice(proxies)
        proxies = self.conn.zrevrange(redis_key, proxy_score_min, proxy_score_max)
        if len(proxies):
            return choice(proxies)

        raise PoolEmptyException

    def decrease(self, proxy: Proxy, redis_key=REDIS_KEY, proxy_score_mix=PROXY_SCORE_MIN):
        """
        在代理检测无效的时候设置分数减1，如果分数达到最低值，那么代理就删除
        :param proxy: proxy, ip:port,like 8.8.8.8:88
        :param redis_key:
        :param proxy_score_mix: 0
        :return: true if successful, false otherwise
        """
        try:
            self.conn.zincrby(redis_key, -1, proxy.string())
            score = self.conn.zscore(redis_key, proxy.string())
            logger_info.info(f"当前proxy:{proxy.string()}，当前分数：{score}")
            if score <= proxy_score_mix:
                self.conn.zrem(redis_key, proxy.string())
        except Exception as e:
            logger_info.info(f"Error deleting key{redis_key}:{e}")
            # print(f"Error deleting key{redis_key}:{e}")
            return False

    def exists(self, proxy: Proxy, redis_key=REDIS_KEY) -> bool:
        """
        判断代理是否存在集合中
        :param proxy: proxy, ip:port,like 8.8.8.8:88
        :param redis_key:
        :return: true
        """
        return not self.conn.zscore(redis_key, proxy.string()) is None

    def max(self, proxy: Proxy, redis_key=REDIS_KEY, proxy_score_max=PROXY_SCORE_MAX):
        """
        用于将代理的分数设置为PROXY_SCORE_MAX
        :param proxy: Proxy, ip:port,like 8.8.8.8:88
        :param redis_key:
        :param proxy_score_max: 100
        :return: new score
        """
        logger_info.info(f"max-分数设置为PROXY_SCORE_MAX......")
        return self.conn.zadd(redis_key, {proxy.string(): proxy_score_max})

    def count(self, redis_key=REDIS_KEY):
        """
        返回当前集合的元素个数
        get count of proxies
        :param redis_key:
        :return: count, int
        """
        return self.conn.zcard(redis_key)

    def all(self, redis_key=REDIS_KEY, proxy_score_min=PROXY_SCORE_MIN, proxy_score_max=PROXY_SCORE_MAX):
        """
        返回所有的代理列表，供检测使用
        get all proxies
        :param redis_key:
        :param proxy_score_min: 0
        :param proxy_score_max: 100
        :return: list of proxies
        """
        return self.conn.zrangebyscore(redis_key, proxy_score_max, proxy_score_min, withscores=True)

    def batch(self, cursor, count, redis_key=REDIS_KEY):
        """
        get batch of proxies
        :param cursor: scan cursor
        :param count: scan count
        :param redis_key:
        :return: list of proxies
        """
        result = []
        cursor, proxies = self.conn.zscan(redis_key, cursor, count=count)
        for i in proxies:
            host, port = i[0].split(':')
            result.append(Proxy(host, int(port)))
        return cursor, result

    def close_connection(self):
        if self.conn:
            del self.conn
            self.conn = None
            logger_info.info(f'Redis Server connection closed.')


if __name__ == '__main__':
    conn = RedisClient()
    # result = conn.get_random()
    # print(result)
    proxy = Proxy('192.168.127.12', 8080)
    test = conn.batch(0, 3)

