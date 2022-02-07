#!/usr/bin/python3.9
from concurrent.futures import process
from pathlib import Path
import os
import src.task

def main():
    for f in os.listdir(src.task.IN_DIR):
        abs_path = Path(src.task.IN_DIR, f)
        task_id = src.task.create_task(abs_path)
        src.task.process_sync(task_id)
    

if __name__ == "__main__":
   main()