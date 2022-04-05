""" test from_file
"""
from pathlib import Path
import shutil
import task, process

TEST_VIDEO_DIR = Path(Path(__file__).parent.parent.parent.parent, 'test_data')

def test_copydata():
    task.create_folders()
    for file in TEST_VIDEO_DIR.iterdir():
        shutil.copy(file, task.IN_DIR)

def test_process():
    process.main()

def test_clear():
    task.clear_folders()