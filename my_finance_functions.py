import pandas as pd
import mstarpy as ms

from mstarpy import search_filter, search_funds


mfund = {
    'FSKAX': {'id': 'F00000MJS0',
             'dist': pd.DataFrame()},
    'FXAIX': {'id': 'F00000LZSI',
             'dist': pd.DataFrame()},
    'ONEQ': {'id': 'FOUSA04BCT',
             'dist': pd.DataFrame()},
    'FBALX': {'id': 'FOUSA00CEL',
             'dist': pd.DataFrame()},
    'FIVLX': {'id': 'FOUSA05HPN',
             'dist': pd.DataFrame()},
    'FSDIX': {'id': 'FOUSA04BQ8',
             'dist': pd.DataFrame()},
    'FSELX': {'id': 'FOUSA00CIJ',
             'dist': pd.DataFrame()},
    'FSMEX': {'id': 'FOUSA00IT1',
             'dist': pd.DataFrame()},
    'FTIHX': {'id': 'F00000WZVM',
             'dist': pd.DataFrame()},
    'FSPSX': {'id': 'F00000MJRM',
             'dist': pd.DataFrame()}
}


bfund = {
    'FSTGX': {'id': 'FOUSA00CHZ'},
    'FCNVX': {'id': 'F00000LQWN'},
    'DOXIX': {'id': 'F00001DHJY'},
    'FIPDX': {'id': 'F00000NZ8Q'},
    'VBTIX': {'id': 'F00000NBIN'}
}

cash_fund = [
    'SPAXX**',
    'FZDXX',
    'FDLXX'
]

all_funds = [mfund, bfund, cash_fund]


def dollar_to_float(row):
    # convert a string with leading "$" to a float
    num = float(row.strip('$'))
    return round(num, 2)


def categorize_position(row):
    # Look at a column of fund tickers and reassign the 'Type' column to tag it appropriately
    if row in mfund:
        return 'Fund'
    elif row in bfund:
        return 'Bond'
    elif row in cash_fund:
        return 'Cash'
    elif row == 'FBTC':
        return 'Bitcoin'
    elif row == '31565A745':
        return 'Other'
    elif len(row) == 9:
        return 'Bond'
    else:
        return 'Other'


def calculate_holdings(mf_ticker, mf_data, portfolio_value):
    mf_data['value'] = mf_data['weighting'] * portfolio_value * 0.01  # Calculate dollar value per holding
    return mf_data.groupby('stock_ticker')['value'].sum().reset_index()  # Sum by stock and reset index


# Function to combine holdings from all mutual funds
def combine_holdings(mf_holdings_dict, portfolio_df):
    combined_holdings = pd.DataFrame()
    for ticker, mf_data in mf_holdings_dict.items():
        # Calculate holdings for each mutual fund
        fund_holdings = calculate_holdings(ticker, mf_data.copy(), portfolio_df.loc[portfolio_df['ticker'] == ticker, 'value'].values[0])
        combined_holdings = pd.concat([combined_holdings, fund_holdings], ignore_index=True)  # Concatenate holdings
    return combined_holdings


def update_fund_distributions(fund_dict, mf_ticker, mf_data):
    for i, ticker in enumerate(fund_dict):

        try:
            shareClassID = mfund[ticker]['id']
            fund = ms.Funds(term=shareClassID, country='us')
            fund_hold = fund.holdings(holdingType='equity')

            # cut down the dataframe to just stock tickers and weightings and drop rows with zero weighting
            fund_hold = fund_hold[['securityName', 'ticker', 'weighting']]
            fund_hold = fund_hold[fund_hold['weighting'].ne(0)]

            # Assign dataframe to 'dist' of the correct fund
            mfund[ticker]['dist'] = fund_hold.copy()

        except KeyError:
            print(f'Iteration {i} failed. Ticker: {ticker}')