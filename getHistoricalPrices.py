import requests
import urllib.parse
import requests
import pandas as pd
import argparse
import configparser

urlhourly = 'https://min-api.cryptocompare.com/data/v2/histohour'
urldaily = 'https://min-api.cryptocompare.com/data/v2/histoday'

CONFIG_FILENAME = 'config.ini'
config = configparser.ConfigParser()
config.read(CONFIG_FILENAME)

def queryHist(fsym, tsym, dp, api_limit, daily, api_key):
    queryParams = {
        'fsym': fsym,
        'tsym': tsym,
        'limit': api_limit,
        'api_key': api_key
    }

    url = urlhourly
    if daily:
        url = urldaily

    dataPoints = dp
    columns = ['time', 'open price']
    data = []
    while True:
        print(f'{dataPoints} to go ...')
        response = requests.get(url, params=queryParams).json()
        tempList = []
        for item in response['Data']['Data']:
            tempList.append((item['time'], item['open']))

        queryParams['toTs'] = tempList[0][0]
        del(tempList[0]) # drop oldest, CryptoCompare returns 2000 + 1 ...
        data = tempList + data

        dataPoints -= queryParams['limit']
        if dataPoints <= 0:
            break
        if dataPoints / api_limit <= 1:
            queryParams['limit'] = dataPoints % api_limit

    filename = fsym + '_' + tsym + '_' + str(dp) + "_%s" %("daily" if daily else "hourly") + '.csv'
    pd.DataFrame.from_records(data, columns=columns).to_csv(path_or_buf=filename, index=False)


def main():
    parser = argparse.ArgumentParser(description='Collect historical pair data from cryptocompare')
    input = parser.add_mutually_exclusive_group()
    parser.add_argument('--fsym', dest='fsym', required=True, help='first of pair')
    parser.add_argument('--tsym', dest='tsym', required=True, help='second of pair')
    parser.add_argument('--limit', dest='limit', nargs='?', default = 2000, const=2000, type=int,
                        help='number of datapoints per API call, max 2k.')
    parser.add_argument('--daily', action='store_true', help='collect daily data, default is hourly')
    parser.add_argument('--example', nargs='?', const=2000, type=int)
    input.add_argument('--dp', dest='dp', type=int, help='Number of data points')
    input.add_argument('--date', dest='date', help='Collect data starting from YYYY-MM-DD')


    args = parser.parse_args()
    if args.dp is None and args.date is None:
        parser.error('at least one of --dp and --date is required')

    api_key = config['CRYPTOCOMPARE_API']['key']
    queryHist(args.fsym, args.tsym, args.dp, args.limit, args.daily, api_key)

if __name__ == "__main__":
    main()

