# Stock_Options_Operation_Screener
Stock Options Operation Screener using MetaTrader 5 to get online data


models.py - SQLAlchemy database model. Example: PETR4 (Petrobras) from Brazilian B3 stock exchange.
app_acquisition.py - Application to extract online information from MetaTrader 5 and store it usingm SQLAlchemy Model.
options_estrategies.py - Extract data from database and MetaTrader 5. Options structures calculation.
options_load.py - Loading Stock data and options information.
PETR4_Options.csv - Option Stock CSV file example.
run_opportunities_monitor.py - This file run getting information from MT5 e running Option's Calculation to return best opportunities.
testing_functions.py - This is the test for all functions of options_estrategies.py

