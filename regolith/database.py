"""Helps manage mongodb setup and connections."""
import subprocess
from contextlib import contextmanager

@contextmanager
def connect(rc):
    proc = subprocess.Popen(['mongod'], universal_newlines=True)
    yield db
    proc.terminate()
