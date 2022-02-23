""" test from_file
"""
from pathlib import Path
import shutil
import task, process

TEST_VIDEO = Path(Path(__file__).parent.parent.parent, 'assets', 'data', 'test.mp4')

def test_copydata():
    task.create_folders()
    shutil.copy(TEST_VIDEO, task.IN_DIR)

def test_process():
    process.main()

def test_clear():
    task.clear_folders()