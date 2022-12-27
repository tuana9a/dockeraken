from dockeraken.configs import cfg
from concurrent.futures import ThreadPoolExecutor

thread_pool = ThreadPoolExecutor(cfg.thread_pool_size)


def create_thread_pool(size=cfg.thread_pool_size):
    return ThreadPoolExecutor(size)
