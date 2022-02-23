import sys

def write_stdout(txt: str):
    print(txt, file=sys.stdout)

def write_stdout_sameline(txt: str):
    print(txt, file=sys.stdout, end='\r')

def write_stderr(txt: str):
    print(txt, file=sys.stderr)