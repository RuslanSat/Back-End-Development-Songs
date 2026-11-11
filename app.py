"""WSGI entry point for Flask CLI and OpenShift's Gunicorn runtime."""
import os
from backend import app

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8080")))
