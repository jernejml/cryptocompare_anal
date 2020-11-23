import requests
import urllib.parse
import requests
import pandas as pd
import argparse
import configparser
import numpy
import math

urlhourly = 'https://min-api.cryptocompare.com/data/v2/histohour'
urldaily = 'https://min-api.cryptocompare.com/data/v2/histoday'

CONFIG_FILENAME = 'config.ini'
config = configparser.ConfigParser()
config.read(CONFIG_FILENAME)

def generalized_volatility_time_hourly_annualized(data):
    prices = [price[1] for price in data]
    #prices = [100, 100.8, 100.3, 100.2, 100.03]
    l = len(prices)
    # step 1
    cont_returns=[]
    for i in range(1, l):
        cont_returns.append(math.log(prices[i]/prices[i-1]))
    # step 2
    n = l-1
    m = sum(cont_returns)/n
    # step 3
    summation = 0
    for i in range(n):
        summation += (cont_returns[i]-m)**2
    s = math.sqrt(summation/(n-1))
    return [l, s, s*math.sqrt(365*24)]



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
    data = []
    while True:
        #print(f'{dataPoints} to go ...')
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

    return data

def main():
    parser = argparse.ArgumentParser(description='Collect historical pair data from cryptocompare')
    input = parser.add_mutually_exclusive_group()
    parser.add_argument('--fsym', dest='fsym', required=True, help='first of pair')
    parser.add_argument('--tsym', dest='tsym', required=True, help='second of pair')
    parser.add_argument('--limit', dest='limit', nargs='?', default = 2000, const=2000, type=int,
                        help='number of datapoints per API call, max 2k.')
    parser.add_argument('--daily', action='store_true', help='collect daily data, default is hourly')
    parser.add_argument('--example', nargs='?', const=2000, type=int)
    parser.add_argument('--volatility', action='store_true', help='calculate generalized volatility for time horizon')
    input.add_argument('--dp', dest='dp', type=int, help='Number of data points')
    input.add_argument('--date', dest='date', help='Collect data starting from YYYY-MM-DD')


    args = parser.parse_args()
    if args.dp is None and args.date is None:
        parser.error('at least one of --dp and --date is required')

    api_key = config['CRYPTOCOMPARE_API']['key']
    data = queryHist(args.fsym, args.tsym, args.dp, args.limit, args.daily, api_key)
    filename = args.fsym + '_' + args.tsym + '_' + str(args.dp) + "_%s" %("daily" if args.daily else "hourly") + '.csv'
    columns = ['time', 'open price']
    pd.DataFrame.from_records(data, columns=columns).to_csv(path_or_buf=filename, index=False)
    if not args.daily and args.volatility:
        v = generalized_volatility_time_hourly_annualized(data)
        print(f'days: {v[0]}')
        print(f'hourly volatility: {round(v[1]*100,2)}%')
        print(f'scaled yearly: {round(v[2]*100,2)}%')



if __name__ == "__main__":
    main()

