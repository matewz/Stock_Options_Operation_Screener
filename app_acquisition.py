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
    
    if datetime.datetime.now().hour >= 10 and datetime.datetime.now().hour <= 17:
        reference_price = mt5.symbol_info_tick(db.PETR4.stock_name).ask
        print("Iniciando Loop -> " + str(db.PETR4.stock_name) + " - Preço: " + str(reference_price))

        last_price = reference_price

        this_month = datetime.datetime.today().date()
        session = db.Session()

        due_dates = session.query(db.PETR4.due_date).distinct().filter(db.PETR4.due_date > datetime.datetime.today()).limit(5)
        due_dates = list(due_dates)

        month_deadline = due_dates[0].due_date
        next_month_dealine = due_dates[1].due_date
        after_next_month_dealine = due_dates[2].due_date
        long_due = due_dates[3].due_date

        diff_betwen_dates = month_deadline - this_month
        if diff_betwen_dates.days < 5:
            month_deadline = next_month_dealine
            next_month_dealine = after_next_month_dealine
            after_next_month_dealine = long_due


        days_to_due_date = (month_deadline - this_month).days

        atm_option = session.query(db.PETR4).filter(db.PETR4.strike <= reference_price, db.PETR4.due_date == month_deadline).order_by(db.PETR4.strike.desc()).first()
        otm_option = session.query(db.PETR4).filter(db.PETR4.strike > reference_price, db.PETR4.due_date == month_deadline).limit(10).all()
        itm_option = session.query(db.PETR4).filter(db.PETR4.strike < reference_price, db.PETR4.due_date == month_deadline).order_by(db.PETR4.strike.desc()).limit(10).offset(1).all()

        next_month_atm_option = session.query(db.PETR4).filter(db.PETR4.strike <= reference_price, db.PETR4.due_date == next_month_dealine).order_by(db.PETR4.strike.desc()).first()
        next_month_otm_option = session.query(db.PETR4).filter(db.PETR4.strike > reference_price, db.PETR4.due_date == next_month_dealine).limit(10).all()
        next_month_itm_option = session.query(db.PETR4).filter(db.PETR4.strike < reference_price, db.PETR4.due_date == next_month_dealine).order_by(db.PETR4.strike.desc()).limit(10).offset(1).all()

        after_next_month_atm_option = session.query(db.PETR4).filter(db.PETR4.strike <= reference_price, db.PETR4.due_date == after_next_month_dealine).order_by(db.PETR4.strike.desc()).first()
        after_next_month_otm_option = session.query(db.PETR4).filter(db.PETR4.strike > reference_price, db.PETR4.due_date == after_next_month_dealine).limit(10).all()
        after_next_month_itm_option = session.query(db.PETR4).filter(db.PETR4.strike < reference_price, db.PETR4.due_date == after_next_month_dealine).order_by(db.PETR4.strike.desc()).limit(10).offset(1).all()


        petr4_options = []

        #stock_price, option, strike,deal_type_zone,due_date,days_to_due_date,timestamp_option,updated_at,last_tick,bid,ask):
        upload_at = datetime.datetime.now()

        def data_store(type, days_to_due_date, option_data):
            for opt in option_data:
                if check_if_symbol_is_selected(opt.option_name) == True:
                    symbol_data = mt5_symbol_info(opt.option_name)
                    data_to_store = db.PETR4_OPTIONS(stock_price=reference_price
                    ,option=opt.option_name, strike=opt.strike ,deal_type_zone=type,due_date=opt.due_date
                    ,days_to_due_date=days_to_due_date,timestamp_option=symbol_data['timestamp']
                    ,updated_at=upload_at,last_tick=symbol_data['last'],bid=symbol_data['bid'],ask=symbol_data['ask'])

                    petr4_options.append(data_to_store)
            
            session.add_all(petr4_options)
            session.commit()

        data_store("ATM",days_to_due_date, [atm_option])
        data_store("OTM",days_to_due_date, otm_option)
        data_store("ITM",days_to_due_date, itm_option)

        data_store("ATM",days_to_due_date, [next_month_atm_option])
        data_store("OTM",days_to_due_date, next_month_otm_option)
        data_store("ITM",days_to_due_date, next_month_itm_option)

        data_store("ATM",days_to_due_date, [after_next_month_atm_option])
        data_store("OTM",days_to_due_date, after_next_month_otm_option)
        data_store("ITM",days_to_due_date, after_next_month_itm_option)

        print("Concluido, aguardando...")
        time.sleep(15)
    else:
        print("Out of work time. Go to home and retire...")
        time.sleep(45)
    # options = {}
# options.update( { atm_option.option_name: { "type": "ATM", "strike": atm_option.strike, "due_date": atm_option.due_date.strftime("%d-%m-%Y"), "days_to_due_date": days_to_due_date, "symbol_info": mt5_symbol_info(atm_option) }})

# for opt in otm_option:
#     if check_if_symbol_is_selected(opt.option_name) == True:
#                 options.update({opt.option_name: { "type": "OTM", "strike": opt.strike, "due_date": opt.due_date.strftime("%d-%m-%Y"), "days_to_due_date": days_to_due_date, "symbol_info": mt5_symbol_info(opt)}})     

# for opt in itm_option:
#     if check_if_symbol_is_selected(opt.option_name) == True:
#             options.update({opt.option_name: { "type": "ITM", "strike": opt.strike, "due_date": opt.due_date.strftime("%d-%m-%Y"), "days_to_due_date": days_to_due_date, "symbol_info": mt5_symbol_info(opt)}})         
