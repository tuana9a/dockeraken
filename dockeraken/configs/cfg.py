import dotenv
import multiprocessing

dotenv.load_dotenv()

cpu_count = multiprocessing.cpu_count()
max_thread_pool_size = 8
min_thread_pool_size = 1
default_thread_pool_size = min(max(cpu_count, 1), 8)

# bash
default_process_timeout_in_seconds = 30

# docker
default_stop_container_timeout_in_seconds = 3 * 60
