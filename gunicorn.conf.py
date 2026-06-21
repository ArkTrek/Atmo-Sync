# Gunicorn configuration file for production load balancing and concurrency scaling
import multiprocessing

# Bind to local network port 5000
bind = "127.0.0.1:5000"

# Compute optimal workers based on CPU cores to scale throughput
workers = multiprocessing.cpu_count() * 2 + 1
threads = 2

# Use gthread worker class to handle keep-alive requests efficiently
worker_class = "gthread"

# Set max pending connections in the TCP queue (backlog)
backlog = 2048

# Kill worker if it hangs for more than 30 seconds
timeout = 30

# Keep-alive timeout for connection reuse
keepalive = 2

# Output standard logging to console
accesslog = "-"
errorlog = "-"
loglevel = "info"
