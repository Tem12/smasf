"""Module contains Mediator class which can run
whole simulation of selfish mining for Nakamoto consensus.

Author: Jan Jakub Kubik (xkubik32)
Date: 17.3.2023
"""
import random

import matplotlib.pyplot as plt

from base.mediator_base import MediatorBase
from base.miner_base import MinerType
from base.sim_config_base import SimulationConfigBase as SimulationConfig
from nakamoto.blockchain import Blockchain
from nakamoto.honest_miner import HonestMinerStrategy
from nakamoto.selfish_miner import SelfishMinerStrategy


def plot_block_counts(block_counts, miners_info):
    """Relevant plot for public blockchain statistics."""
    miner_names = list(block_counts.keys())
    total_blocks = sum(block_counts.values())
    block_percentages = [
        100 * block_counts[name] / total_blocks for name in miner_names
    ]

    mining_powers = miners_info
    mining_power_labels = [f"{100 * power:.1f}%" for power in mining_powers]

    bars = plt.bar(miner_names, block_percentages)

    for bar_new, label, miner_name in zip(bars, mining_power_labels, miner_names):
        height = bar_new.get_height()
        block_count = block_counts[miner_name]
        plt.text(
            bar_new.get_x() + bar_new.get_width() / 2,
            height,
            f"{label}\n{block_count} blocks",
            ha="center",
            va="bottom",
            fontsize=10,
        )

    plt.xlabel("Miner")
    plt.ylabel("Percentage of Blocks Mined")
    plt.title(
        f"Percentage of Blocks Mined by Each Miner (Mining Power and Block "
        f"Count on Top of Bars)\nTotal Blocks: {total_blocks}"
    )
    plt.show()


class Mediator(MediatorBase):
    """Mediator class for Nakamoto consensus for running whole simulation."""

    def __init__(self, simulation_config: dict, blockchain: str):
        super().__init__(simulation_config, blockchain)
        self.honest_miner = HonestMinerStrategy(mining_power=self.config.honest_miner)
        self.selfish_miners = [
            SelfishMinerStrategy(mining_power=sm_power)
            for sm_power in self.config.selfish_miners
        ]
        self.public_blockchain = Blockchain(owner="public blockchain")

    def parse_config(self, simulation_config):
        """Parsing dict from yaml config."""
        self.log.info("Nakamoto parse config method")

        # check main keys
        expected_keys = {
            "consensus_name",
            "miners",
            "gamma",
            "simulation_mining_rounds",
        }
        sim_config = list(simulation_config.values())[0]
        self.validate_blockchain_config_keys(sim_config, expected_keys)

        print(sim_config)
        miners = sim_config["miners"]
        if len(list(miners["honest"])) != 1:
            raise ValueError("You must setup exactly 1 honest miner")
        if len(list(miners["selfish"])) == 0:
            raise ValueError("You must setup at least 1 selfish miner")

        honest_miner = miners["honest"]["mining_power"]
        selfish_miners = [sm["mining_power"] for sm in miners["selfish"]]
        return SimulationConfig(
            consensus_name=sim_config["consensus_name"],
            honest_miner=honest_miner,
            selfish_miners=selfish_miners,
            gamma=sim_config["gamma"],
            simulation_mining_rounds=sim_config["simulation_mining_rounds"],
        )

    @staticmethod
    def weighted_random_choice(choices, weights):
        """Select according weights leader of current round."""
        return random.choices(choices, weights, k=1)[0]

    # pylint: disable=too-many-statements
    # pylint: disable=too-many-branches
    def run(self):
        """Entry point for running all checks for specific provider monitor."""
        self.log.info("Mediator in Nakamoto")
        print(self.config)

        print("Honest miner")
        print("=========" * 50)
        print(self.honest_miner)
        print(self.honest_miner.__dict__)
        print("Selfish miners")
        print("=========" * 50)
        for selfish_miner in [sm.__dict__ for sm in self.selfish_miners]:
            print(selfish_miner)

        miners = [self.honest_miner] + self.selfish_miners
        miners_info = [self.honest_miner.mining_power] + [
            sm.mining_power for sm in self.selfish_miners
        ]
        print(miners)
        print(miners_info)

        blocks_mined = 0
        ongoing_fork = False
        orphaned_blocks = []

        while blocks_mined < self.config.simulation_mining_rounds:
            leader = self.weighted_random_choice(miners, miners_info)
            blocks_mined += 1

            if leader.miner_type == MinerType.SELFISH:  # selfish miner found a block
                self.log.info(
                    f"Selfish miner {leader.miner_id} is leader of round {blocks_mined}"
                )
                if leader.blockchain.size() == 0:  # no local blockchain
                    leader.blockchain.fork_block_id = (
                        self.public_blockchain.last_block_id
                    )
                    leader.blockchain.add_block(
                        f"Block {blocks_mined} data", f"Selfish miner {leader.miner_id}"
                    )
                else:
                    leader.blockchain.add_block(
                        f"Block {blocks_mined} data", f"Selfish miner {leader.miner_id}"
                    )
                    if ongoing_fork:
                        ongoing_fork = False
                        self.log.info("Override by attacker in fork")
                        self.log.info(leader.blockchain.fork_block_id)
                        self.public_blockchain.chain[
                            leader.blockchain.fork_block_id - 1 :
                        ] = []
                        orphaned_blocks.extend(
                            self.public_blockchain.chain[
                                : leader.blockchain.fork_block_id
                            ]
                        )

                        self.public_blockchain.chain.extend(leader.blockchain.chain)
                        leader.blockchain.chain = []
                        leader.blockchain.fork_block_id = None

            elif leader.miner_type == MinerType.HONEST:  # honest miner found a block
                self.log.info(
                    f"Honest miner {leader.miner_id} is leader of round {blocks_mined}"
                )
                one_sm = self.selfish_miners[0]
                if ongoing_fork:
                    ongoing_fork = False
                    if self.config.gamma == 0.5:
                        res = leader.mining_power * 0.5 / 100
                        print(res)
                        # exit()
                        if random.random() <= res:
                            print("Previous block won selfish miner")
                            orphaned_blocks.append(self.public_blockchain.chain[-1])
                            self.public_blockchain.chain[-1] = one_sm.blockchain.chain[
                                -1
                            ]
                            one_sm.blockchain.chain = []
                            one_sm.blockchain.fork_block_id = None

                self.public_blockchain.add_block(
                    f"Block {blocks_mined} data", f"Honest miner {leader.miner_id}"
                )

                if one_sm.blockchain.size() > 0:
                    chain_difference = (
                        one_sm.blockchain.length()
                        - self.public_blockchain.last_block_id
                    )
                    self.log.info(
                        f"Private chain length: {one_sm.blockchain.size()}, "
                        f"fork start: {one_sm.blockchain.fork_block_id}"
                    )
                    self.log.info(f"Chain difference is: {chain_difference}")

                    if chain_difference >= 2:
                        # wait action should be published block - but not necessary
                        self.log.info("Nothing to do ....")

                    elif chain_difference == 1:
                        self.log.info("Override.")
                        self.log.info(one_sm.blockchain.fork_block_id)
                        self.public_blockchain.chain[
                            one_sm.blockchain.fork_block_id - 1 :
                        ] = []
                        orphaned_blocks.extend(
                            self.public_blockchain.chain[
                                : one_sm.blockchain.fork_block_id
                            ]
                        )
                        self.public_blockchain.chain.extend(one_sm.blockchain.chain)
                        one_sm.blockchain.chain = []
                        one_sm.blockchain.fork_block_id = None

                    elif chain_difference == 0:
                        self.log.info("Match.")
                        if self.config.gamma == 1:  # integrate selfish last block
                            self.log.info("SM wins")
                            orphaned_blocks.append(self.public_blockchain.chain[-1])
                            self.public_blockchain.chain[-1] = one_sm.blockchain.chain[
                                -1
                            ]
                            one_sm.blockchain.chain = []
                            one_sm.blockchain.fork_block_id = None

                        elif self.config.gamma == 0:  # nothing to do wins honest miner
                            self.log.info("HM ???.")
                            ongoing_fork = True
                            # orphaned_blocks.append(one_sm.blockchain.chain[-1])
                            # one_sm.blockchain.chain = []
                            # one_sm.blockchain.fork_block_id = None

                        elif self.config.gamma == 0.5:
                            ongoing_fork = True

                    else:
                        self.log.info("Adopt honest miner is winning.")
                        ongoing_fork = False
                        one_sm.blockchain.chain = []
                        one_sm.blockchain.fork_block_id = None

                else:
                    self.log.info("Private chain has 0 length --> nothing to do")

            else:
                raise Exception("Something is very wrong.")

        # print('Public blockchain:')
        # self.log.info(self.public_blockchain.chain)
        # print('Orphans')
        # self.log.info([o for o in orphaned_blocks])

        miners = [self.public_blockchain, self.selfish_miners[0].blockchain]
        block_counts = {
            "Honest miner 42": 0,
            "Selfish miner 43": 0,
        }
        print(block_counts)

        print(block_counts)
        for block in self.public_blockchain.chain:
            print(block)
            block_counts[block.miner] += 1

        print(block_counts)
        # print(self.selfish_miners[0].blockchain.chain)

        plot_block_counts(block_counts, miners_info)
