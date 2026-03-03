"""
Production entry point — serves the app with Waitress.

Usage:
    python run.py

Waitress is a production-grade pure-Python WSGI server.
It handles multiple threads and does not expose the Flask
debug interface or reloader.

For development, use:
    python app.py
"""
from waitress import serve
from app import app

if __name__ == '__main__':
    print("Starting StudySync with Waitress on http://0.0.0.0:5000")
    serve(app, host='0.0.0.0', port=5000, threads=4)
