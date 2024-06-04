import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)8.8s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logging.getLogger("azure").setLevel(logging.ERROR)
logger = logging.getLogger(__name__)
