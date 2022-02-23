#!/usr/bin/python3.9
from pathlib import Path
import os
from time import sleep
import task

def main():
    for f in os.listdir(task.IN_DIR):
        abs_path = Path(task.IN_DIR, f)
        task.create_task(abs_path)
    for task_id in task.get_tasks():
        task.process_sync(task_id)
        

if __name__ == "__main__":
   main()