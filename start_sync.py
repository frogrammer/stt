#!/usr/bin/python3.9
from concurrent.futures import process
from pathlib import Path
import os
from time import sleep
import src.task

def main():
    while True:
        for f in os.listdir(src.task.IN_DIR):
            abs_path = Path(src.task.IN_DIR, f)
            src.task.create_task(abs_path)
        for task_id in src.task.get_tasks():
            src.task.process_sync(task_id)
        sleep(15)
        

if __name__ == "__main__":
   main()