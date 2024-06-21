# Portfolio Optimization Web Application

This project aims to optimize a stock portfolio based on user-defined constraints and objectives, leveraging historical stock data and financial metrics like alpha and beta. The application includes a web interface for user input and a backend server for processing the portfolio optimization. The tool is currently curated to give results for NSE listed stocks.

## Table of Contents

- [Demo](#demo)
- [Features](#features)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
  - [Frontend](#frontend)
  - [Backend](#backend)
- [Optimization Details](#optimization-details)
- [Technologies Used](#technologies-used)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgements](#acknowledgements)
- [Contact](#contact)

## Demo

![Option Optimization Web Application](./PortfolioOptimization.gif)

## Features

- **User Input Form:** Enter stock tickers, date range, target beta, and weight constraints.
- **Optimization Objective:** Maximize portfolio alpha while considering a target beta or simply maximizing portfolio alpha.
- **Fixed Weights:** Option to specify fixed weights for certain stocks if required.
- **Industry Weightage:** Breakdown of portfolio weights by industry.
- **Detailed Results:** Display optimized weights, alpha, beta, and returns.

## Getting Started

### Prerequisites

- Python 3.7 or higher
- Flask
- Flask-CORS
- yfinance
- numpy
- scipy
- pandas
- axios (for frontend HTTP requests)

### Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/portfolio-optimization.git
    cd portfolio-optimization
    ```

2. Set up a virtual environment:
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

4. Run the Flask server:
    ```bash
    python app.py
    ```

## Usage

### Frontend

The frontend is a simple HTML form that allows users to input their stock tickers, date range, target beta, and other constraints. The form data is sent to the Flask backend for processing.

### Backend

The backend is a Flask application that handles portfolio optimization using the provided parameters. It fetches historical stock data from Yahoo Finance, calculates alpha and beta for each stock, and optimizes the portfolio using the `scipy.optimize.minimize` function.

## Optimization Details

The optimization aims to maximize the portfolio alpha while maintaining the target beta or simply maximizing portfolio alpha without beta restrictions. It uses the `scipy.optimize.minimize` function with constraints on the minimum and maximum weights for each stock. The optimization also considers fixed weights if provided.

## Technologies Used

- **Frontend:** HTML, CSS, JavaScript (Axios for HTTP requests)
- **Backend:** Python, Flask, Flask-CORS, yfinance, numpy, scipy, pandas

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

## License

This project is licensed under the MIT License.

## Acknowledgements

- [Yahoo Finance](https://www.yahoofinance.com) for providing historical stock data.
- [Flask](https://flask.palletsprojects.com/) for the web framework.
- [scipy.optimize](https://docs.scipy.org/doc/scipy/reference/optimize.html) for the optimization algorithm.

 ## Contact

 Please feel free to contact me on aryanchoudhari09@gmail.com for any feedback, queries or suggestions.
