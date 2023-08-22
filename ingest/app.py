import argparse
from sys import argv

from api import WCLApiClient
from cfg import Config
from db import PGClient
from etl import ETL
from log import get_logger


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-g", "--guild")
    parser.add_argument("-H", "--historical", action="store_true")
    return parser.parse_args()


def main():
    get_logger().info("Started processing...")

    args = parse_args()

    guild_name = None
    if args.guild:
        guild_name = args.guild
        get_logger().info(f"Processing single guild: {guild_name}")

    get_logger().info("Initializing PGSQL Client...")
    pg_client = PGClient()
    get_logger().info("Initializing WCL Api Client...")
    api_client = WCLApiClient()
    get_logger().info("Loading configs...")
    cfg = Config(pg_client, guild_name)
    get_logger().info("Initializing Ingestor...")
    ETL(
        cfg,
        api_client,
        pg_client,
        args.historical
    ).extract_and_transform() \
     .load()
    get_logger().info("Finished processing...")


if __name__ == "__main__":
    main()

