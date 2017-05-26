#!/usr/bin/python

import math
import logging
import sys
import threading
import time
import datetime

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
    logging.basicConfig(level=logging.INFO)

class CPU_Bound:
    def __init__(self, tid, factorial_ns, reps):
        self.factorial_ns = factorial_ns
        self.reps = reps
        self.total_tasks = math.fsum(reps)
        self.completed_tasks = 0
        self.tid = tid

    def execute(self):
        for i in xrange(len(self.factorial_ns)):
            factorial_n = self.factorial_ns[i]
            rep = self.reps[i]
            for j in xrange(rep):
                math.factorial(factorial_n)
                self.completed_tasks += 1
                print self.completed_tasks
                time.sleep(1)

def main():    
    log_file_path = sys.argv[1]
    n_threads = int(sys.argv[2])
    
    logger = Log("progress_log", log_file_path)
    configure_logging()
    
    # Build execution script from arguments
    factorial_ns = []
    reps = []
    for i in xrange(3, len(sys.argv), 2):
        factorial_n = int(sys.argv[i])
        rep = int(sys.argv[i + 1])
        factorial_ns.append(factorial_n)
        reps.append(rep)

    # Create threads
    cbs = []
    threads = []
    for i in xrange(n_threads):
        cb = CPU_Bound(i, factorial_ns, reps)
        f_thread = threading.Thread(target=cb.execute)
        threads.append(f_thread)
        cbs.append(cb)
    
    total_tasks = n_threads*math.fsum(reps)

    # Start threads
    for thread in threads:
        thread.start()
        
    completed = 0
    
    # Get progress and wait for completion
    while completed < total_tasks:
        completed = 0    
        for i in xrange(n_threads):
            completed += cbs[i].completed_tasks
        progress = completed/total_tasks
        timestamp = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        logger.log("[%s][Progress]: #%f" % (timestamp, progress))
        time.sleep(1)

if __name__ == '__main__':
    main()