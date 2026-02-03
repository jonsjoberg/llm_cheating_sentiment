import sys
import logging
log_level = logging.INFO  # Change INFO to DEBUG for verbose logging
log_format = '%(asctime)s  %(levelname)-8s %(message)s'
log_date_format = '%Y-%m-%d %H:%M:%S'

log = logging.getLogger(__name__)
logging.basicConfig(
    stream=sys.stdout,
    level=log_level,
    format=log_format,
    datefmt=log_date_format
)
