from concurrent.futures import ThreadPoolExecutor
from threading import Semaphore
from src.config.config import concurrency_config

# Create thread pool for credibility calculations
credibility_executor = ThreadPoolExecutor(
    max_workers=concurrency_config.CREDIBILITY_MAX_THREADS
)

# Create semaphore for limiting concurrent operations
credibility_semaphore = Semaphore(concurrency_config.CREDIBILITY_MAX_CONCURRENT)

def cleanup_resources():
    """Cleanup all concurrent resources"""
    credibility_executor.shutdown(wait=True)
