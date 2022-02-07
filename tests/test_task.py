""" test from_file
"""
from pathlib import Path
import shutil
import src.task

TEST_VIDEO = Path(Path(__file__).parent, 'assets', 'test.mp4')

def test_process():
    src.task.create_folders()
    shutil.copy(TEST_VIDEO, src.task.IN_DIR)
    task_id = src.task.create_task(str(Path(src.task.IN_DIR, TEST_VIDEO.name)))
    src.task.process_sync(task_id)