from math import factorial
from time import sleep
import sys
import threading
import random
from time import time
import logging

class Log:
    def __init__(self, name, output_file_path):
        self.logger = logging.getLogger(name)
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        self.logger.addHandler(handler)
        handler = logging.FileHandler(output_file_path)
        self.logger.addHandler(handler)

    def log(self, text):
        self.logger.info(text)

def configure_logging():
    logging.basicConfig(level=logging.DEBUG)

def main(n_threads, n_factorial_min, n_factorial_max, n_loop, time_sleep_min, time_sleep_max, stress_trigger, stress_value, logger, progress_logger):
    for i in xrange(n_threads):
        factorial_thread = threading.Thread(target=factorial_loop,
                                            args=(i, n_factorial_min, n_factorial_max,
                                                  n_loop, time_sleep_min, time_sleep_max,
                                                  stress_trigger, stress_value,
                                                  logger, progress_logger))

        factorial_thread.start()

def factorial_loop(thread_number, n_factorial_min, n_factorial_max, n_loop, time_sleep_min,
                    time_sleep_max, stress_trigger, stress_value, logger, progress_logger):
    logger.log("Starting thread: %d" % (thread_number))

    for i in xrange(n_loop):
        factorial_value = random.randrange(n_factorial_min, n_factorial_max)
        sleep_value = random.randrange(time_sleep_min, time_sleep_max)

        if factorial_value > stress_trigger:
            factorial_value = stress_value

        start = time()
        factorial(factorial_value)
        end = time()
        elapsed_time = end - start

        progress_logger.log("%d,%d,%f" % (thread_number, i + 1, elapsed_time))
        logger.log("thread=%d|loop-i=%d|factorial-n=%d|time_sleep=%d" % (thread_number, i + 1,
                                                                        factorial_value, sleep_value))

        sleep(float(sleep_value))


if __name__ == '__main__':
    n_threads = int(sys.argv[1])
    time_sleep_min = int(sys.argv[2])
    time_sleep_max = int(sys.argv[3])
    n_factorial_min = int(sys.argv[4])
    n_factorial_max = int(sys.argv[5])
    n_loop = int(sys.argv[6])
    stress_trigger = int(sys.argv[7])
    stress_value = int(sys.argv[8])

    logger = Log("log", "log.txt")
    progress_logger = Log("progress-log", "progress.txt")
    configure_logging()

    logger.log("Using conf: n_threads=%d, time_sleep=[%d,%d], n_factorial=[%d,%d], n_loop=%d"
                        % (n_threads, time_sleep_min, time_sleep_max,
                           n_factorial_min, n_factorial_max, n_loop))

    main(n_threads, n_factorial_min, n_factorial_max, n_loop, time_sleep_min, time_sleep_max, stress_trigger, stress_value, logger, progress_logger)


