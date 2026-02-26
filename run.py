"""Convenience runner for the project.

Usage:
  python run.py web       # start the API server
  python run.py worker    # start the worker (falls back to DB polling)

This script ensures the inner package directory is on sys.path so imports like
`from db import SessionLocal` work when running from the repository root.
"""
import sys
import os
import subprocess

ROOT = os.path.dirname(__file__)
APP_DIR = os.path.join(ROOT, 'financial-document-analyzer-debug')

if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)


def run_uvicorn():
    cmd = [sys.executable, '-m', 'uvicorn', 'main:app', '--app-dir', 'financial-document-analyzer-debug', '--host', '127.0.0.1', '--port', '8000', '--reload']
    print('Running:', ' '.join(cmd))
    subprocess.run(cmd)


def run_worker():
    cmd = [sys.executable, os.path.join('financial-document-analyzer-debug', 'worker.py')]
    print('Running worker:', ' '.join(cmd))
    subprocess.run(cmd)


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('cmd', choices=['web', 'worker'], help='command to run')
    args = p.parse_args()

    if args.cmd == 'web':
        run_uvicorn()
    elif args.cmd == 'worker':
        run_worker()


if __name__ == '__main__':
    main()
