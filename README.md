In this project, we develop a simple circuit to create, back test and deploy strategies. 
Using the Interactive Brokers API to get data and do the deployment, we do the following steps:
- We fix a certain market
- Using a very small portion of the data, we try different strategies (like trend-following and mean reversion)
- We optimize the strategies, with slippage and comissions included, doing a walk-forward optimization, viewing a set of metrics (mainly Sharpe Ratio)
- Robustness tests: Monte Carlo simulations (resampling data), sensitivity analysis of parameters and tests in multiple correlated markets
- Position sizing: we adjust the position to achieve a certain volatility target, and a Monte-Carlo Drawdown analysis
- Portfolio: we adjust the weights of each strategy depending on the correlation between them
- Post-deploy: we deploy it in a demo account and analyze the progress, comparing it to previous tests
