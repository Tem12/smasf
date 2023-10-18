import pandas as pd
import numpy as np
import json
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=str, required=True, help='Input file path')
    parser.add_argument('--tag', type=str, required=True, help='Tag')
    parser.add_argument('--block_reward', type=int, required=True, help='Block reward multiplier')
    args = parser.parse_args()

    block_reward = args.block_reward  # times of fruits
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
    # for miner in miners:
        # fruit_count[miner] = 0

    print(miners)
    print(fruit_count)

    total_reward_from_all = 0

    # print('Fruits:')
    for index, row in df.iterrows():
        fruit_rewards = json.loads(row['fruits'])
        unique, counts = np.unique(fruit_rewards, return_counts=True)
        i = 0
        for miner in unique:
            if miner not in fruit_count:
                fruit_count[miner] = 0
            fruit_count[miner] += counts[i]
            i += 1
        # for miner in miners:
            # fruit_count[miner] += fruit_rewards.count(miner)

    print('Before block count')
    print(fruit_count)

    # print(f'Total (with block {block_reward}x reward):')
    total_reward = {}
    for index, row in df.iterrows():
        if row['miner_id'] not in fruit_count:
            fruit_count[row['miner_id']] = 0
        fruit_count[row['miner_id']] += block_reward

    # Block are also stored in fruit_count
    print('After block count')
    print(fruit_count)

    for _, val in fruit_count.items():
        total_reward_from_all += val

    # for i in range(0, len(block_counts)):
    #     # Add block rewards
    #     val = block_counts.values[i] + (fruit_count[miners[i]] / block_reward)
    #     total_reward[miners[i]] = val
    #     total_reward_from_all += val

    print(total_reward)

    print(f'Total reward from all: {total_reward_from_all}')

    perc = {}
    for key, val in fruit_count.items():
        perc_reward = val / total_reward_from_all * 100
        perc[str(key)] = perc_reward

    # perc = {}
    # for key, val in total_reward.items():
    #     perc[str(key)] = (val / total_reward_from_all * 100)

    print(perc)

    with open(f"{args.tag}.json", "w") as file:
        json.dump(perc, file)

if __name__ == "__main__":
    main()