"""Module providingFunction printing python version.

Author: Jan Jakub Kubik (xkubik32)
Date: 12.3.2023
"""
import argparse

from base.logs import create_logger


def parse_args():
    """Parse all program arguments."""
    parser = argparse.ArgumentParser(
        description="Simulate selfish mining on different blockchains."
    )
    parser.add_argument(
        "blockchain",
        choices=["nakamoto", "subchain", "strongchain", "fruitchain"],
        type=str,
        help="Select blockchain network where you want to simulate selfish mining",
    )

    return parser.parse_args()


def main():
    """Main function of whole program."""
    args = parse_args()
    print(args.blockchain)
    #  rozvetvenie podla args
    # yaml configy
    # try how is working nested logging

    log = create_logger("main")
    log.info("logging")
    print(log)


if __name__ == "__main__":
    main()
