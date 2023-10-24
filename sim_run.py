from concurrent.futures import ProcessPoolExecutor
import subprocess
from datetime import datetime
import time
import numpy as np
import argparse
import yaml

# ================= USER SPACE =================

# ----- General settings -----

# Maximum number of running concurrent simulations
MAX_INSTANCES = 2

# How many times should be simulations repeated with same configuration
EXPERIMENT_REPEAT = 10

# Gamma settings for all simulation, must be same
GAMMA = 0.0

MINING_ROUNDS = 500

# Selfish miners power
num_of_cfgs = (
    3
)  # Optional variable, can be removed and specified directly in np.linespace
SELFISH_MINERS = [
    np.linspace(
        5, 40, num_of_cfgs, dtype=int
    ),  # 1. miner has power 5, 10, 15, ... 40, (len = 8)
    np.linspace(
        10, 10, num_of_cfgs, dtype=int
    )  # 2. miner has power 10, 10, 10, ... 10, (len = 8)
    # add another selfish miners with np.linspace if needed
]

# # Example:
# num_of_cfgs = 40 // 5
# SELFISH_MINERS = [
#     np.linspace(5, 40, num_of_cfgs),    # 1. miner has power 5, 10, 15, ... 40, (len = 8)
#     np.linspace(10, 10, num_of_cfgs)    # 2. miner has power 10, 10, 10, ... 10, (len = 8)
#     # add another selfish miners with np.linspace if needed
# ]

# Honest miner is added automatically

# ----- Fruitchain settings -----
FRUIT_MINE_PROB = 0.9
SUPERBLOCK_MINE_PROB = 0.1

# ----- Strongchain settings -----
WEAK_TO_STRONG_HEADER_RATIO = 100


# ==============================================

experiment_counter = 0
finished_simulations = 0
total_simulations = 0

program_args = None

config_unique_prefix = ""


def main():
    global program_args
    global config_unique_prefix

    global total_simulations
    global finished_simulations

    parser = argparse.ArgumentParser(
        description="Selfish mining simulator - automated simulation execution"
    )
    parser.add_argument(
        "blockchain",
        choices=["fruitchain", "strongchain"],
        type=str,
        help="Chain to simulate",
    )
    parser.add_argument("--out", type=str, required=True, help="Output files prefix")

    args = parser.parse_args()
    program_args = args

    config_unique_prefix = round(time.time() * 1000)

    simulations = None

    if args.blockchain == "fruitchain":
        simulations, res_count_simulations = create_fruitchain_simulation_queue()
    elif args.blockchain == "strongchain":
        simulations = create_strongchain_simulation_queue()
    
    total_simulations = len(simulations)

     # Log number of launched simulations
    date_time = datetime.now().strftime('%m-%d-%Y %H:%M:%S')
    print(f'[{date_time}] Queued: {total_simulations} simulations, running on {MAX_INSTANCES} CPUs')

    # Start simulations on separate CPUs
    with ProcessPoolExecutor(max_workers=MAX_INSTANCES) as executor:
        while len(simulations) > 0:
            sim = simulations.pop(0)
            future = executor.submit(run_simulation, sim)
            future.add_done_callback(log_finished_simulation)

    if (args.blockchain == "fruitchain"):
        total_simulations += len(res_count_simulations)
        print('Post process part started...')
        # Start simulations on separate CPUs
        with ProcessPoolExecutor(max_workers=MAX_INSTANCES) as executor:
            while len(res_count_simulations) > 0:
                sim = res_count_simulations.pop(0)
                future = executor.submit(run_simulation, sim)
                future.add_done_callback(log_finished_simulation)


def create_miners_settings():
    if len(SELFISH_MINERS) < 1:
        error_exit("No seflish miner specified")

    expected_cfg_length = len(SELFISH_MINERS[0])
    honest_mining_power = np.array([], dtype=int)
    all_selfish_mining_power = np.array([], dtype=int)

    for cfgs in SELFISH_MINERS:
        if len(cfgs) != expected_cfg_length:
            error_exit(
                "Array length of mining power of individual selfish miners differs"
            )

    for j in range(0, expected_cfg_length):
        power = 0
        for i in range(0, len(SELFISH_MINERS)):
            power += SELFISH_MINERS[i][j]

        if power > 100:
            error_exit("Invalid mining power for selfish miners")

        all_selfish_mining_power = np.append(all_selfish_mining_power, power)
        honest_mining_power = np.append(honest_mining_power, 100 - power)

    return all_selfish_mining_power, honest_mining_power


def create_fruitchain_simulation_queue():
    simulations = []
    res_count_simulations = []

    all_selfish_mining_power, honest_mining_power = create_miners_settings()

    print('Simulation powers:')
    print(f'All selfish: {all_selfish_mining_power}')
    print(f'Honest: {honest_mining_power}')

    # Create all required configs
    for i in range(0, len(all_selfish_mining_power)):
        fruit_yaml = [
            {
                "simulation1": {
                    "consensus_name": "Fruitchain",
                    "miners": {
                        "honest": {"mining_power": int(honest_mining_power[i])},
                        "selfish": [{"mining_power": int(SELFISH_MINERS[j][i])} for j in range(0, len(SELFISH_MINERS))],
                    },
                    "gamma": GAMMA,
                    "simulation_mining_rounds": MINING_ROUNDS,
                    "fruit_mine_prob": FRUIT_MINE_PROB,
                    "superblock_prob": SUPERBLOCK_MINE_PROB,
                }
            }
        ]

        with open(f"/tmp/fruitchain_cfg_{config_unique_prefix}_{i}.yaml", "w") as file:
            yaml.dump(fruit_yaml, file)

    run_base = [f"python3", "main.py"]
    res_count_base = [f"python3", "res_count.py"]

    for experiment_i in range(0, EXPERIMENT_REPEAT):
        for i in range(0, len(all_selfish_mining_power)):
            simulations.append(
                run_base
                + [
                    "--out",
                    f"{program_args.out}_{i}_{experiment_i}.out",
                    "fruitchain",
                    "--config",
                    f"/tmp/fruitchain_cfg_{config_unique_prefix}_{i}.yaml",
                ]
            )

        for i in range(0, len(all_selfish_mining_power)):
            res_count_simulations.append(
                res_count_base
                + [
                    "--input",
                    f"{program_args.out}_{i}_{experiment_i}.out",
                    "--tag",
                    f"{program_args.out}_{i}_{experiment_i}",
                    "--block_reward",
                    f"{int(SUPERBLOCK_MINE_PROB / (FRUIT_MINE_PROB + SUPERBLOCK_MINE_PROB) * 100)}"
                ]
            )

    return simulations, res_count_simulations

def create_strongchain_simulation_queue():
    simulations = []

    all_selfish_mining_power, honest_mining_power = create_miners_settings()

    print('Simulation powers:')
    print(f'All selfish: {all_selfish_mining_power}')
    print(f'Honest: {honest_mining_power}')

    # Create all required configs
    for i in range(0, len(all_selfish_mining_power)):
        fruit_yaml = [
            {
                "simulation1": {
                    "consensus_name": "Strongchain",
                    "miners": {
                        "honest": {"mining_power": int(honest_mining_power[i])},
                        "selfish": [{"mining_power": int(SELFISH_MINERS[j][i])} for j in range(0, len(SELFISH_MINERS))],
                    },
                    "simulation_mining_rounds": MINING_ROUNDS,
                    "weak_to_strong_header_ratio": WEAK_TO_STRONG_HEADER_RATIO
                }
            }
        ]

        with open(f"/tmp/strongchain_cfg_{config_unique_prefix}_{i}.yaml", "w") as file:
            yaml.dump(fruit_yaml, file)

    run_base = [f"python3", "main.py"]

    for experiment_i in range(0, EXPERIMENT_REPEAT):
        for i in range(0, len(all_selfish_mining_power)):
            simulations.append(
                run_base
                + [
                    "--out",
                    f"{program_args.out}_{i}_{experiment_i}.out",
                    "strongchain",
                    "--config",
                    f"/tmp/strongchain_cfg_{config_unique_prefix}_{i}.yaml",
                ]
            )

    return simulations


def run_simulation(simulation):
    subprocess.run(simulation, stdout=subprocess.DEVNULL)


def log_finished_simulation(_):
    global finished_simulations
    finished_simulations += 1
    date_time = datetime.now().strftime('%m-%d-%Y %H:%M:%S')
    print(f'[{date_time}] Finished: {finished_simulations}/{total_simulations}')


def error_exit(msg):
    print(f"Error: {msg}")
    exit(1)


if __name__ == "__main__":
    main()
