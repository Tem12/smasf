"""Module contains Mediator class which can run
whole simulation of selfish mining for Nakamoto consensus.

Author: Jan Jakub Kubik (xkubik32)
Date: 17.3.2023
"""
from base.mediator_base import ActionObjectStore, MediatorBase
from base.miner_base import HonestMinerAction as HA
from base.miner_base import SelfishMinerAction as SA
from base.sim_config_base import SimulationConfigBase as SimulationConfig
from nakamoto.blockchain import Blockchain
from nakamoto.honest_miner import HonestMinerStrategy
from nakamoto.my_graphs import plot_block_counts
from nakamoto.selfish_miner import SelfishMinerStrategy


class Mediator(MediatorBase):
    """Mediator class for Nakamoto consensus for running whole simulation."""

    def __init__(self, simulation_config: dict, blockchain: str):
        super().__init__(simulation_config, blockchain)
        self.honest_miner = HonestMinerStrategy(mining_power=self.config.honest_miner)
        self.selfish_miners = [
            SelfishMinerStrategy(mining_power=sm_power)
            for sm_power in self.config.selfish_miners
        ]
        self.miners = [self.honest_miner] + self.selfish_miners
        self.miners_info = [self.honest_miner.mining_power] + [
            sm.mining_power for sm in self.selfish_miners
        ]
        self.public_blockchain = Blockchain(owner="public blockchain")
        self.action_store = ActionObjectStore()
        self.ongoing_fork = False

    def __parse_config(self, simulation_config):
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

    def __resolve_matches(self, match_competitors, ongoing_fork):
        # !!! WORKS just for 1 attacker
        match_obj = self.action_store.get_objects(SA.MATCH)[0]

        self.log.info("resolve match")
        if self.config.gamma == 1:  # integrate selfish last block
            self.log.info("SM wins")
            self.public_blockchain.chain[-1] = match_obj.blockchain.chain[-1]
            match_obj.blockchain.chain = []
            match_obj.blockchain.fork_block_id = None

        elif self.config.gamma == 0:
            self.ongoing_fork = True

        elif self.config.gamma == 0.5:
            self.ongoing_fork = True

    def __resolve_overrides(self):
        self.log.info("resolve_overrides")
        # !!! WORKS just for 1 attacker
        match_obj = self.action_store.get_objects(SA.OVERRIDE)[0]
        self.public_blockchain.chain[match_obj.blockchain.fork_block_id - 1 :] = []

        self.public_blockchain.chain.extend(match_obj.blockchain.chain)
        match_obj.blockchain.chain = []
        match_obj.blockchain.fork_block_id = None
        self.action_store.remove_object(SA.OVERRIDE, match_obj)

    def run_simulation(self):
        """Main business logic for running selfish mining simulation."""
        match_competitors = set()  # competitors with match actions

        for blocks_mined in range(self.config.simulation_mining_rounds):
            leader = self.choose_leader(self.miners, self.miners_info)
            self.ongoing_fork = leader.mine_new_block(
                blocks_mined,
                self.public_blockchain,
                self.ongoing_fork,
                match_competitors,
                self.config.gamma,
            )
            action = leader.get_and_reset_action()

            if not self.ongoing_fork and action == SA.WAIT:
                # end current mining round
                continue

            if action == SA.OVERRIDE:
                # override public blockchain by attacker's private blockchain
                self.ongoing_fork = False
                self.log.info(
                    f"Override by attacker {leader.blockchain.fork_block_id} in fork"
                )
                self.public_blockchain.chain[leader.blockchain.fork_block_id - 1 :] = []
                self.public_blockchain.chain.extend(leader.blockchain.chain)
                leader.blockchain.chain = []
                leader.blockchain.fork_block_id = None

            elif action == HA.PUBLISH:
                # honest miner has already published a new block to public blockchain
                pass

            # elif action == SA.MATCH:
            #     # TDO: viac utocnikov - prebieha fork a vytazil dalsi s fork matchom
            #     pass

            self.action_store.clear()
            while True:  # currently 1 time run
                for selfish_miner in self.selfish_miners:

                    if (
                        selfish_miner.miner_id
                        != self.public_blockchain.chain[-1].miner_id
                    ):
                        action = selfish_miner.decide_next_action(
                            self.public_blockchain, leader
                        )
                        self.action_store.add_object(action, selfish_miner)

                all_actions = self.action_store.get_actions()

                if SA.OVERRIDE in all_actions:
                    self.__resolve_overrides()

                elif SA.MATCH in all_actions:
                    self.__resolve_matches(match_competitors, self.ongoing_fork)
                    match_competitors.add(self.selfish_miners[0])
                    break  # end mining round

                if SA.OVERRIDE not in all_actions:
                    # Instead of do while
                    if self.ongoing_fork:
                        self.ongoing_fork = False

                    break

                self.action_store.clear()

    def run(self):
        self.log.info("Mediator in Nakamoto")

        self.run_simulation()

        block_counts = {
            "Honest miner 42": 0,
            "Selfish miner 43": 0,
        }
        self.log.info(block_counts)

        self.log.info(block_counts)
        for block in self.public_blockchain.chain:
            self.log.info(block)
            block_counts[block.miner] += 1

        self.log.info(block_counts)
        self.log.info(self.selfish_miners[0].blockchain.chain)

        plot_block_counts(block_counts, self.miners_info)
