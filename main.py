"""Main module of whole program.

Author: Jan Jakub Kubik (xkubik32)
Date: 12.3.2023
"""
import argparse

from base.logs import create_logger
from fruitchain.mediator import run as fruitchain_run
from nakamoto.mediator import run as nakamoto_run
from strongchain.mediator import run as strongchain_run
from subchain.mediator import run as subchain_run


def parse_args():
    """Parse all program arguments."""
    parser = argparse.ArgumentParser(
        description="Simulate selfish mining on different blockchains."
    )
    parser.add_argument(
        "blockchain",
        choices=["nakamoto", "subchain", "strongchain", "fruitchain"],
        type=str.lower,
        help="Select blockchain network where you want to simulate selfish mining",
    )

    return parser.parse_args()


def main():
    """Main function of whole program."""
    args = parse_args()
    if args.blockchain == "nakamoto":
        nakamoto_run()
    elif args.blockchain == "subchain":
        subchain_run()
    elif args.blockchain == "strongchain":
        strongchain_run()
    else:
        fruitchain_run()

    # yaml configy
    # try how is working nested logging

    log = create_logger("main")
    log.info("logging")
    print(log)


if __name__ == "__main__":
    main()
