import pandas as pd
import numpy as np
import json
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=str, required=True, help='Input file path')
    parser.add_argument('--tag', type=str, required=True, help='Tag')
    args = parser.parse_args()

    block_reward = 10  # times of fruits
    df = pd.read_csv(args.input)
    block_counts = df['miner_id'].value_counts()
    # block_counts = block_counts.sort_index(ascending=True)

    print('Miners:')
    print(block_counts.keys().values)

    print('Blocks (count):')
    print(block_counts.values)

    miners = block_counts.keys().values
    # miners.sort()

    # Resolve fruit count
    fruit_count = {}
    for miner in miners:
        fruit_count[miner] = 0

    print(miners)
    print(fruit_count)

    # print('Fruits:')
    for index, row in df.iterrows():
        fruit_rewards = json.loads(row['fruits'])
        for miner in miners:
            fruit_count[miner] += fruit_rewards.count(miner)

    print(fruit_count)

    # print(f'Total (with block {block_reward}x reward):')
    total_reward = {}
    total_reward_from_all = 0
    for i in range(0, len(block_counts)):
        # Add block rewards
        val = block_counts.values[i] + (fruit_count[miners[i]] / block_reward)
        total_reward[miners[i]] = val
        total_reward_from_all += val

    print(total_reward)

    print(f'Total reward from all: {total_reward_from_all}')
    perc = {}
    for key, val in total_reward.items():
        perc[str(key)] = (val / total_reward_from_all * 100)

    print(perc)

    with open(f"{args.tag}.json", "w") as file:
        json.dump(perc, file)

if __name__ == "__main__":
    main()