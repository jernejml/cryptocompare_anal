# cryptocompare_anal

- rename config_template.ini to config.ini
- add your cryptocompare API key
- use help for input instructions:
  - "python getHistoricalPrices.py -h" 
  - "python getDownsideRiskStats.py -h"
- use python 3.x 

Examples:
python.exe getHistoricalPrices.py --fsym REN --tsym USD --dp 1000

python.exe getHistoricalPrices.py --fsym UNI --tsym USD --dp 60 --daily

python.exe getDownsideRiskStats.py --fsym UNI --tsym USD --days 60 --width 5 --max 40

python.exe getDownsideRiskStats.py --fsym REN --tsym USD --days 90 --width 5 --max 60



