# custom logging functionality

import os
import sys
import logging

# save time, level name, module, and message of log
logging_str = "[%(asctime)s: %(levelname)s: %(module)s: %(message)s]"

# create a logs directory with a file to save the log info
log_dir = "logs"
log_filepath = os.path.join(log_dir,"running_logs.logs")
os.makedirs(log_dir, exist_ok=True)

# define log configuration
logging.basicConfig(
  level=logging.INFO, 
  format=logging_str,
  handlers=[
    logging.FileHandler(log_filepath), # logs saved to the file created
    logging.StreamHandler(sys.stdout)  # logs saved also go to stdout
  ]
)

logger = logging.getLogger("mlopsLogger")