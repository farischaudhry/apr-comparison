import requests
import pandas as pd
from dune_client.client import DuneClient
import matplotlib.pyplot as plt

def main():
    # Initialize the Dune client with your API key
    dune = DuneClient("3QM48n5GsHs5KZpneRb87uY3mywzlGjn")
    merged_df = merge_bal_data()
    print(merged_df)

def save_dune_query_to_csv(dune, query_id, filename):
    query_result = dune.get_latest_result(query_id)
    data_rows = query_result.result.rows
    df = pd.DataFrame(data_rows)
    df.to_csv(filename, index=False)

def fetch_bal_prices(dune):
    save_dune_query_to_csv(dune, 3931901, 'bal/daily_price_data.csv')

def fetch_bal_supply(dune):
    save_dune_query_to_csv(dune, 543807, 'bal/supply_data.csv')

def fetch_bal_apr(dune):
    save_dune_query_to_csv(dune, 3939002, 'bal/apr_data.csv')

def merge_bal_data():
    '''
    Returns a dataframe with the Balancer (BAL) data.
    '''
    # Load the data from CSV files
    price_df = pd.read_csv('bal/daily_price_data.csv').drop_duplicates()
    supply_df = pd.read_csv('bal/supply_data.csv').drop_duplicates()
    apr_df = pd.read_csv('bal/apr_data.csv').drop_duplicates()

    # Rename columns as per the previous discussion
    price_df = price_df.rename(columns={'time': 'timestamp', 'avg_price': 'price'})
    supply_df = supply_df.rename(columns={
        'day': 'timestamp',
        'locked': 'bonded_supply',
        'locked_pct': 'bonded_percent',
        'total': 'total_supply'
    })
    apr_df = apr_df.rename(columns={'day': 'timestamp', 'rev_per_bal_locked': 'apr'})
    supply_df['circ_supply'] = supply_df['total_supply'] - supply_df['bonded_supply']
    supply_df = supply_df[['timestamp', 'total_supply', 'circ_supply', 'bonded_supply', 'bonded_percent']]

    # Calculate the daily inflation rate
    supply_df = supply_df.sort_values(by='timestamp', ascending=True)
    supply_df['daily_inflation_rate'] = supply_df['total_supply'].pct_change()

    # Convert timestamp columns to datetime
    price_df['timestamp'] = pd.to_datetime(price_df['timestamp'], utc=True)
    supply_df['timestamp'] = pd.to_datetime(supply_df['timestamp'], utc=True)
    apr_df['timestamp'] = pd.to_datetime(apr_df['timestamp'], utc=True)

    price_df['timestamp'] = price_df['timestamp'].dt.strftime('%Y-%m-%d')
    supply_df['timestamp'] = supply_df['timestamp'].dt.strftime('%Y-%m-%d')
    apr_df['timestamp'] = apr_df['timestamp'].dt.strftime('%Y-%m-%d')

    # Merge the dataframes
    merged_df = pd.merge(price_df, supply_df, on='timestamp', how='outer') \
                  .merge(apr_df, on='timestamp', how='outer')


    merged_df = merged_df.sort_values(by='timestamp', ascending=True)
    merged_df.set_index('timestamp', inplace=True)
    merged_df['has_liquid_staking'] = False

    return merged_df.dropna()


if __name__ == "__main__":
    main()
