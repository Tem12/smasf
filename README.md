# SMASF - Selfish Mining Attacks Simulation Framework

Welcome to SMASF, a robust simulation framework dedicated to the exploration
and analysis of selfish mining attacks with one, two, and multiple attackers
in various blockchain consensus protocols. My goal was to provide the community
with an easily extensible framework designed to assess the impact of selfish mining
attacks. This tool serves as a platform for testing existing systems and
assisting in the development of new, more secure consensus protocols.

Currently, supported consensus protocols are:

+ Nakamoto -- [link to paper](https://bitcoin.org/bitcoin.pdf)
+ Subchain -- [link to paper](https://ledgerjournal.org/ojs/index.php/ledger/article/view/40)
+ Strongchain -- [link to paper](https://www.usenix.org/conference/usenixsecurity19/presentation/szalachowski)

## Table of Contents

+ [Installation](#installation)
+ [Usage](#usage)
+ [Workflow Diagrams](#workflow-diagrams)
+ [Simulation Experiments](#simulation-experiments)
+ [Contributing](#contributing)

## Installation

To begin using SMASF, you must first set up a Python virtual environment.
Throughout the framework's development, Python 3.8 was the version used.
Upon setting up the virtual environment, the next step is to install all
necessary Python packages with the following command:

```bash
pip install -r requirements.txt
```

Although I considered containerizing SMASF, it currently doesn't seem
essential for its use cases. However, the option for easy containerization
remains open for future development.

## Usage

Each consensus protocol is configurable through YAML files in their respective
directories. These files allow you to set the mining power of each miner,
selfish or honest, as well as the number of simulation rounds. The gamma
parameter is adjustable for Nakamoto and Subchain protocols, while
Subchain also supports weak-to-strong block ratios, and Strongchain uses
weak-to-strong header ratios. To execute a simulation, install the necessary
packages, set the configuration (or use default values), and run main.py
with the following parameters:

```bash
python main.py --help

usage: main.py [-h] {subchain,nakamoto,strongchain} ...

Simulate selfish mining on different blockchains.

positional arguments:
  {subchain,nakamoto,strongchain}
    subchain         Subchain simulation with mandatory 'weak' or 'strong'
    nakamoto            Nakamoto blockchain simulation
    strongchain         Strongchain blockchain simulation

optional arguments:
  -h, --help            show this help message and exit
```

## Workflow Diagrams

Each supported consensus protocol was developed according to proposed
workflow diagram, which describes the behavior of all important entities
for selfish mining (miners, blockchain and simulation manager).
These workflow diagrams are available online for all supported consensus
protocols:

+[Nakamoto consensus workflow diagram](https://miro.com/app/board/uXjVMeBFZw8=/?share_link_id=254956633663)
+[Subchain consensus workflow diagrams](https://miro.com/app/board/uXjVMaBHSA8=/?share_link_id=48031802517)
+[Strongchain consensus workflow diagram](https://miro.com/app/board/uXjVMZAjw5U=/?share_link_id=459699217455)

## Simulation Experiments

I performed two types of experiments. The first was for finding thresholds from where
the selfish mining for individual consensus protocol became profitable, and the second
is for observing selfish mining development with different configurations for an
attacker/attackers. The results of these experiments for supported consensus
protocols are available online:

+ [Nakamoto consensus experiments](https://docs.google.com/spreadsheets/d/1r0Z_4taUu02thfOkYR5kpf8HQZtsEOo_rOAvAe1AEfY/edit?usp=sharing)
+ [Subchain consensus experiments](https://docs.google.com/spreadsheets/d/1a80sRPVeCZLRKrEKM773YdYKN81VQ0mvEjrtVyps9TE/edit?usp=sharing)
+ [Strongchain consensus experiments](https://docs.google.com/spreadsheets/d/11LNUFQWlYa0BoNCNpiqozMAT0ijv4Eowrk6TKHE95MM/edit?usp=sharing)

## Contributing

Interested in contributing to SMASF? I welcome your input.
Follow these steps to contribute:

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Submit a pull request with a problem description
