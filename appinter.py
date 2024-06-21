from flask import Flask, request, jsonify
from flask_cors import CORS
import yfinance as yf
import numpy as np
from scipy.optimize import minimize
import pandas as pd

app = Flask(__name__)
CORS(app)

def get_industry_info(stock_symbols):
    industry_info = {}
    for symbol in stock_symbols:
        try:
            stock = yf.Ticker(symbol)
            industry = stock.info['industry']
            industry_info[symbol] = industry
        except Exception as e:
            industry_info[symbol] = f"Error: {str(e)}"
    return industry_info

def get_portfolio_optimization(tickers, start_date, end_date, target_beta, min_weight, max_weight, maximize_alpha=True, fixed_weights=None):
    try:
        data = yf.download(tickers, start=start_date, end=end_date)['Adj Close']
        pd.set_option('display.max_columns', None)  # Show all columns
        pd.set_option('display.max_rows', None)     # Show all rows
        print(f"{pd.DataFrame(data[tickers])}")
    except Exception as e:
        return {'error': f"Error fetching data from Yahoo Finance: {e}"}
    
    nan_tickers = data.columns[data.isna().any()].tolist()
    data = data.drop(columns=nan_tickers)
    
    if data.empty:
        return {'error': 'All provided tickers contain NaN values. Please provide valid tickers.'}
    
    tickers = data.columns.tolist()
    returns = data.pct_change().dropna()

    market_ticker = '^NSEI'
    try:
        market_data = yf.download(market_ticker, start=start_date, end=end_date)['Adj Close']
    except Exception as e:
        return {'error': f"Error fetching market data from Yahoo Finance: {e}"}
    
    market_returns = market_data.pct_change().dropna()

    # Align the dates to the common range
    common_dates = returns.index.intersection(market_returns.index)
    market_returns = market_returns.loc[common_dates]
    returns = returns.loc[common_dates]

    alphas = {}
    betas = {}
    returns_sum = returns.sum()
    stock_return_percents = {}

    for ticker in tickers:
        stock_returns = returns[ticker]
        stock_returns_pct = (((data[ticker].iloc[-1] - data[ticker].iloc[0]) / data[ticker].iloc[0]) * 100).round(2)
        market_return_percent = (((market_data.iloc[-1] - market_data.iloc[0]) / market_data.iloc[0]) * 100).round(2)
        alpha = stock_returns_pct - market_return_percent
        market_returns_array = market_returns.values.flatten()
        beta = np.cov(stock_returns, market_returns_array)[0, 1] / np.var(market_returns_array)
        alphas[ticker] = alpha
        betas[ticker] = beta
        stock_return_percents[ticker] = stock_returns_pct


    alpha_values = np.array(list(alphas.values()))
    beta_values = np.array(list(betas.values()))

    def objective(weights):
        portfolio_beta = np.dot(weights, beta_values)
        portfolio_alpha = np.dot(weights, alpha_values)
        
        if maximize_alpha:
            objective_value = -portfolio_alpha
        else:
            penalty = 1000 * (portfolio_beta - target_beta)**3
            objective_value = -portfolio_alpha + penalty
        
        return objective_value

    constraints = [
        {'type': 'eq', 'fun': lambda weights: np.sum(weights) - 1},
        {'type': 'ineq', 'fun': lambda weights: max_weight - weights}
    ]
    bounds = [(min_weight, 1) for _ in range(len(tickers))]

    if fixed_weights:
        fixed_indices = []
        fixed_values = []
        for ticker, weight in fixed_weights.items():
            index = tickers.index(ticker)
            fixed_indices.append(index)
            fixed_values.append(weight / 100)
        
        constraints.append({'type': 'eq', 'fun': lambda weights: np.array([weights[i] for i in fixed_indices]) - np.array(fixed_values)})

    initial_guess = [1 / len(tickers)] * len(tickers)
    result = minimize(objective, initial_guess, bounds=bounds, constraints=constraints)

    if not result.success:
        return {'error': f"Optimization failed: {result.message}"}

    optimal_weights = result.x
    portfolio_alpha = np.dot(optimal_weights, alpha_values)
    portfolio_beta = np.dot(optimal_weights, beta_values)

    percent_weights = optimal_weights * 100

    alpha_values_percent = (alpha_values).round(2).tolist()
    beta_values_rounded = beta_values.round(2).tolist()
    portfolio_alpha_percent = (portfolio_alpha).round(2)
    portfolio_beta_rounded = portfolio_beta.round(2)

    industry_weights_percent = get_industry_weights(tickers, percent_weights)

    sorted_by_industry = {}
    for ticker, weight, alpha, beta in zip(tickers, percent_weights, alpha_values_percent, beta_values_rounded):
        industry = get_industry_info([ticker]).get(ticker, "Unknown")
        stock_info = {
            'ticker': ticker,
            'weight': round(weight, 2),
            'alpha': alpha,
            'beta': beta,
            'stock_return_percent': stock_return_percents[ticker]
        }
        
        if industry not in sorted_by_industry:
            sorted_by_industry[industry] = []
        sorted_by_industry[industry].append(stock_info)

    portfolio_return_percent = portfolio_alpha_percent + market_return_percent

    optimal_portfolio = {
        'tickers': tickers,
        'weights_percent': [round(wp, 2) for wp in percent_weights.tolist()],
        'alpha_percent': alpha_values_percent,
        'beta': beta_values_rounded,
        'portfolio_alpha_percent': portfolio_alpha_percent,
        'portfolio_beta': portfolio_beta_rounded,
        'target_beta': round(target_beta, 2),
        'market_return_percent': market_return_percent,
        'portfolio_return_percent': portfolio_return_percent,
        'industry_weights_percent': industry_weights_percent,
        'sorted_by_industry': sorted_by_industry,
        'excluded_tickers': nan_tickers
    }
    print(alpha_values_percent)
    return optimal_portfolio

def get_industry_weights(tickers, weights):
    industry_info = get_industry_info(tickers)
    industry_weights = {}
    for ticker, weight in zip(tickers, weights):
        industry = industry_info.get(ticker)
        if industry not in industry_weights:
            industry_weights[industry] = 0
        industry_weights[industry] += weight

    return {industry: round(weight, 2) for industry, weight in industry_weights.items()}

@app.route('/optimize', methods=['POST'])
def optimize_portfolio():
    if request.method == 'POST':
        req_data = request.get_json()
        tickers = req_data.get('tickers', [])
        start_date = req_data.get('start_date')
        end_date = req_data.get('end_date')
        target_beta = req_data.get('target_beta', 1)
        min_weight = float(req_data.get('min_weight', 5)) / 100
        max_weight = float(req_data.get('max_weight', 30)) / 100
        maximize_alpha = req_data.get('maximize_alpha', True)
        fixed_weights = req_data.get('fixed_weights', {})

        if not tickers:
            return jsonify({'error': 'No stock tickers provided'}), 400

        result = get_portfolio_optimization(tickers, start_date, end_date, target_beta, min_weight, max_weight, maximize_alpha, fixed_weights)
        return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
