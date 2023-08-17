from cfg import ReportConfig
from log import get_logger
from report import WCLBrazilReport


def main():
    get_logger().info("Started processing...")
    WCLBrazilReport().load() \
                     .calculate_rankings() \
                     .save()
    get_logger().info("Finished processing...")


if __name__ == "__main__":
    main()

