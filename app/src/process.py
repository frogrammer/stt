#!/usr/bin/python3.9
from concurrent.futures import process
from pathlib import Path
import os
import task

def main():
    for f in os.listdir(task.IN_DIR):
        abs_path = Path(task.IN_DIR, f)
        task_id = task.create_task(abs_path)
        task.process_sync(task_id)
    

if __name__ == "__main__":
   main()