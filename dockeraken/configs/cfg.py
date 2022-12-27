import multiprocessing

cpu_count = multiprocessing.cpu_count()
max_thread_pool_size = 8
min_thread_pool_size = 2
thread_pool_size = min(max(cpu_count, min_thread_pool_size),
                       max_thread_pool_size)

# docker
stop_container_timeout_in_seconds = 3 * 60

# rabbitmq connection string
transport_url: str = ""

# setup id
dockeraken_id: str = ""
