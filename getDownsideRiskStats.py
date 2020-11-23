import requests
import urllib.parse
import requests
import argparse
import pandas as pd
import configparser

CONFIG_FILENAME = 'config.ini'
config = configparser.ConfigParser()
config.read(CONFIG_FILENAME)


def query_data(fsym, tsym, days, api_key):
    query_params = {
        'fsym': fsym,
        'tsym': tsym,
        'limit': days,
        'api_key': api_key
    }
    url = 'https://min-api.cryptocompare.com/data/v2/histoday'
    return requests.get(url, params=query_params).json()


def fill_bucket(response, decrement, max, fsym):

    keys_percentage = list(range(decrement, max + decrement, decrement))
    keys = [i/100 for i in keys_percentage]
    keys.reverse()
    reverse_keys_percentage = keys_percentage.copy()
    reverse_keys_percentage.reverse()
    drop_bucket = {}
    for k in reverse_keys_percentage:
        drop_bucket[str(-k) + "%"] = 0
    for daystats in response['Data']['Data']:
        if daystats['close'] >= daystats['open']:
            continue
        drop = (daystats['open'] - daystats['close']) / daystats['open']
        for k, r in zip(keys, reverse_keys_percentage):
            if drop > k:
                drop_bucket[str(-r) + "%"] += 1
                break
    bucket = {}
    #bucket[fsym] = {}
    key_list = list(drop_bucket.keys())
    key_list.reverse()
    for k in key_list:
        bucket[k] = drop_bucket[k]
        #bucket[fsym][k] = drop_bucket[k]
    return bucket


def main():
    parser = argparse.ArgumentParser(description='Collect historical pair data from cryptocompare')
    parser.add_argument('--fsym', dest='fsym', required=True, help='first of pair')
    parser.add_argument('--tsym', dest='tsym', required=True, help='second of pair')
    parser.add_argument('--limit', dest='limit', nargs='?', default=2000, const=2000, type=int,
                        help='number of datapoints per API call, max 2k.')
    parser.add_argument('--days', dest='days', required=True, help='Number of days backwards')
    parser.add_argument('--width', dest='width', required=True, type=int, help='bucket width or step|decrement')
    parser.add_argument('--max', dest='max', required=True, type=int, help='last bucket percentage or lower bound|max drop')

    args = parser.parse_args()
    api_key = config['CRYPTOCOMPARE_API']['key']
    response = query_data(args.fsym, args.tsym, args.days, api_key)
    bucket = fill_bucket(response, args.width, args.max, args.fsym)
    filename = args.fsym + '_' + args.tsym + '_' + str(args.width) + '_' + str(args.max) + '.csv'

    pd.DataFrame(list(bucket.items()), columns=[args.fsym, 'count']).to_csv(path_or_buf=filename, index=False)


if __name__ == "__main__":
    main()

