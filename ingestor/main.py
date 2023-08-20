from sys import argv

from api import WCLApiClient
from cfg import IngestionConfig
from db import PGClient
from log import get_logger
from ingest import WCLBrazilIngestor


def main():
    get_logger().info("Started processing...")

    guild_name = None
    if len(argv) > 1:
        guild_name = argv[1]
        get_logger().info(f"Processing single guild: {guild_name}")\

    get_logger().info("Initializing PGSQL Client...")
    pg_client = PGClient()
    get_logger().info("Loading configs...")
    cfg = IngestionConfig(pg_client, guild_name)
    get_logger().info("Initializing WCL Api Client...")
    api_client = WCLApiClient()
    get_logger().info("Initializing Ingestor...")
    WCLBrazilIngestor(cfg, api_client, pg_client).extract_and_transform() \
                                                 .load()
    get_logger().info("Finished processing...")


if __name__ == "__main__":
    main()

