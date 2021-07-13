import MetaTrader5 as mt5
import models as db
import datetime
import pandas as pd
from sqlalchemy import extract
import time

if not mt5.initialize():
    print("initialize() failed")
    mt5.shutdown()

symbols=mt5.symbols_get()

list_of_all_symbols = []
list_of_visible_symbols = []

for item in symbols:
    list_of_all_symbols.append(item.name)
    
def check_if_symbol_is_selected(symbol):
    if symbol in list_of_visible_symbols:
        return True
    
    if symbol in list_of_all_symbols:
        for item in symbols:
            if item.name == symbol:
                if item.visible == True:
                    list_of_visible_symbols.append(item.name)
                    return True
                else:
                    return False
    else:
        False

def mt5_symbol_info(symbol):
    info = { "timestamp": datetime.datetime.utcfromtimestamp(mt5.symbol_info_tick(symbol).time).strftime('%Y-%m-%d %H:%M:%S'), "last": mt5.symbol_info_tick(symbol).last,  "bid": mt5.symbol_info_tick(symbol).bid , "ask": mt5.symbol_info_tick(symbol).ask }
    return info


while 1:
    reference_price = mt5.symbol_info_tick(db.PETR4.stock_name).ask

    last_price = reference_price

    this_month = datetime.datetime.today().date()
    month_deadline = db.session.query(db.PETR4).filter(extract('month', db.PETR4.due_date) == datetime.datetime.today().month).first().due_date

    diff_betwen_dates = month_deadline - this_month
    if diff_betwen_dates.days < 2:
        month_deadline = db.session.query(db.PETR4).filter(extract('month', db.PETR4.due_date) == datetime.datetime.today().month+1).first().due_date

    days_to_due_date = (month_deadline - this_month).days

    atm_option = db.session.query(db.PETR4).filter(db.PETR4.strike <= reference_price, db.PETR4.due_date == month_deadline).order_by(db.PETR4.strike.desc()).first()
    otm_option = db.session.query(db.PETR4).filter(db.PETR4.strike > reference_price, db.PETR4.due_date == month_deadline).limit(10).all()
    itm_option = db.session.query(db.PETR4).filter(db.PETR4.strike < reference_price, db.PETR4.due_date == month_deadline).order_by(db.PETR4.strike.desc()).limit(10).offset(1).all()

    petr4_options = []

    #stock_price, option, strike,deal_type_zone,due_date,days_to_due_date,timestamp_option,updated_at,last_tick,bid,ask):
    upload_at = datetime.datetime.now()

    def data_store(type, days_to_due_date, option_data):
        for opt in option_data:
            symbol_data = mt5_symbol_info(opt.option_name)
            data_to_store = db.PETR4_OPTIONS(stock_price=reference_price
            ,option=opt.option_name, strike=opt.strike ,deal_type_zone=type,due_date=opt.due_date
            ,days_to_due_date=days_to_due_date,timestamp_option=symbol_data['timestamp']
            ,updated_at=upload_at,last_tick=symbol_data['last'],bid=symbol_data['bid'],ask=symbol_data['ask'])

            petr4_options.append(data_to_store)
        
        db.session.add_all(petr4_options)
        db.session.commit()

    data_store("ATM",days_to_due_date, [atm_option])
    time.sleep(15)

    # options = {}
# options.update( { atm_option.option_name: { "type": "ATM", "strike": atm_option.strike, "due_date": atm_option.due_date.strftime("%d-%m-%Y"), "days_to_due_date": days_to_due_date, "symbol_info": mt5_symbol_info(atm_option) }})

# for opt in otm_option:
#     if check_if_symbol_is_selected(opt.option_name) == True:
#                 options.update({opt.option_name: { "type": "OTM", "strike": opt.strike, "due_date": opt.due_date.strftime("%d-%m-%Y"), "days_to_due_date": days_to_due_date, "symbol_info": mt5_symbol_info(opt)}})     

# for opt in itm_option:
#     if check_if_symbol_is_selected(opt.option_name) == True:
#             options.update({opt.option_name: { "type": "ITM", "strike": opt.strike, "due_date": opt.due_date.strftime("%d-%m-%Y"), "days_to_due_date": days_to_due_date, "symbol_info": mt5_symbol_info(opt)}})         
