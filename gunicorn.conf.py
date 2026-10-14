import os

# Render dynamically assigns a PORT environment variable (typically 10000)
port = os.environ.get("PORT", "5000")
bind = f"0.0.0.0:{port}"

# Optimize workers and threads for Render free tier (512MB RAM)
workers = int(os.environ.get("WEB_CONCURRENCY", "2"))
threads = 4
timeout = 120
keepalive = 5

# Stream logs directly to stdout/stderr so they show in Render dashboard
accesslog = "-"
errorlog = "-"
loglevel = "info"
