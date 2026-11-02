import logging

logging.basicConfig(
    filename="air_quality.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8",
    force=True
)

logger = logging.getLogger("air_quality")

logging.getLogger("watchfiles").setLevel(logging.WARNING)