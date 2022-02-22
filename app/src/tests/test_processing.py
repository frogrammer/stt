""" test from_file
"""
from pathlib import Path
import shutil
import task

TEST_VIDEO = Path(Path(__file__).parent.parent.parent.parent, 'assets', 'test.mp4')

def test_process():
    task.create_folders()
    shutil.copy(TEST_VIDEO, task.IN_DIR)
    task_id = task.create_task(str(Path(task.IN_DIR, TEST_VIDEO.name)))
    task.process_sync(task_id)

def test_clear():
    task.clear_folders()