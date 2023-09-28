import pandas as pd
import json


def main():
    block_reward = 1  # times of fruits
    df = pd.read_csv('fruit_res.csv')
    block_counts = df['miner_id'].value_counts()

    print('Miners:')
    print(block_counts.keys().values)

    print('Blocks (count):')
    print(block_counts.values)

    miners = block_counts.keys().values

    # Resolve fruit count
    fruit_count = {}
    for miner in miners:
        fruit_count[miner] = 0

    print('Fruits:')
    for index, row in df.iterrows():
        fruit_rewards = json.loads(row['fruits'])
        for miner in miners:
            fruit_count[miner] += fruit_rewards.count(miner)

    print(fruit_count)

    print(f'Total (with block {block_reward}x reward):')
    total_reward = []
    for i in range(0, len(block_counts)):
        # Add block rewards
        total_reward.append(block_counts.values[i] * block_reward + fruit_count[miners[i]])

    print(total_reward)

    print('Total percentage:')
    total_reward_from_all = sum(total_reward)
    perc = []
    for count in total_reward:
        perc.append(count / total_reward_from_all * 100)

    print(perc)


if __name__ == "__main__":
    main()
