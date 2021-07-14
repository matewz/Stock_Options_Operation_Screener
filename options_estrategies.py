from sqlalchemy import extract, desc
import datetime
import models as db
import time
import MetaTrader5 as mt5
import pandas as pd
from enum import Enum


class Option_Due(Enum):
    This_Month = 1
    Next_Month = 2
    After_Month = 3

class ButterFly_Mode(Enum):
    Real_Time = 1
    Offline = 2

    
class options_estrategies():

    if not mt5.initialize():
        print("initialize() failed")
        mt5.shutdown()
    
    def __init__(self):
        pass

    def get_book_and_return_first_line(self, symb):
        #get ASK and BID price and volume
        #returning BookInfo
        mt5.market_book_add(symb)
        time.sleep(0.1)
        items = mt5.market_book_get(symb)
        mt5.market_book_release(symb)  
        if len(items) > 0:
            for l in range(0,len(items)):
                if l > 0:
                    if items[l].type != items[l-1].type:
                        return {'bid': items[l], 'ask': items[l-1]}

        # bid - [BookInfo(type=2, price=1.02, volume=41100, volume_dbl=41100.0),
        # ask - [BookInfo(type=1, price=1.07, volume=41100, volume_dbl=41100.0)]

    
    def check_butterfly_realtime(self, tick_data, cost_limit = 1, show_broken_wings = False):
        
        # math = buy 1 -> sell 2 next strike -> buy 1 after next
        # return how much you need to pay to mount this structur
        # if negative you receive money to create it
        # check if butterfly have symmetric wings
        
        model_return = []
        for i in range(0,len(tick_data)-2):
            assymetric_wings = 0
            
            #check if are symmetric wings
            diff_wings = tick_data[i].strike - (2 * tick_data[i + 1].strike) + tick_data[i + 2].strike
            
            #tic = time.perf_counter()
            wing_1 = self.get_book_and_return_first_line(tick_data[i].option_name)
            wing_2 = self.get_book_and_return_first_line(tick_data[i+1].option_name)
            wing_3 = self.get_book_and_return_first_line(tick_data[i+2].option_name)
            #toc = time.perf_counter()
            #print(f"Time to request data {toc - tic:0.4f} seconds")

            if wing_1 != None:
                wing_1_price = wing_1['ask'].price
                wing_1_volume = wing_1['ask'].volume
            else: 
                wing_1_price = tick_data[i].ask
                wing_1_volume = 0
                if float(wing_1_price) == 0:
                    continue
                    
            if wing_2 != None:
                wing_2_price = wing_2['bid'].price
                wing_2_volume = wing_2['bid'].volume
            else: 
                wing_2_price = tick_data[i+1].bid
                wing_2_volume = 0
                if float(wing_2_price) == 0:
                    continue           

            if wing_3 != None:
                wing_3_price = wing_3['ask'].price
                wing_3_volume = wing_3['ask'].volume
                if float(wing_3_price) == 0:
                    continue
            else: 
                wing_3_price = tick_data[i+2].ask
                wing_3_volume = 0
                if float(wing_3_price) == 0:
                    continue
                

            cost =  round(wing_1_price - (2 * wing_2_price) + wing_3_price,2)
            
            max_profit = round((tick_data[i + 1].strike - tick_data[i].strike) - cost,2)
            stock_price = float(tick_data[i].stock_price)
            percent_to_max_profit = round(((tick_data[i + 1].strike - stock_price) / stock_price)*100,2)
            max_loss = cost
            
            if diff_wings > 0 and show_broken_wings == False:
                break
            else:
                max_loss = cost
                
            if cost < cost_limit:
                max_volume = min([wing_1_volume,wing_2_volume,wing_3_volume])
                #'{}:{}:{}'.format('teste','1','ou')
                butterfly_symbols = '{}: {}, {}: {}, {}:{} '.format(tick_data[i].option_name
                                                    , wing_1_price
                                                    , tick_data[i + 1].option_name
                                                    , wing_2_price
                                                    , tick_data[i + 2].option_name
                                                    , wing_3_price)
                model_return.append(
                    {
                    'BUTTERFLY': butterfly_symbols
                    , "COST": cost             
                    , "MAX_PROFIT": max_profit
                    , "MAX_LOSS": max_loss
                    , "MAX_VOLUME" : max_volume                    
                    , "DIFF_BETWEEN_WINGS": diff_wings
                    , "PERCENT_2_MAX_PAYOFF":percent_to_max_profit
                    })

        return model_return


    def check_butterfly_database(self, tick_data, cost_limit = 1, show_broken_wings = False):
        
        # math = buy 1 -> sell 2 next strike -> buy 1 after next
        # return how much you need to pay to mount this structur
        # if negative you receive money to create it
        # check if butterfly have symmetric wings
        
        model_return = []
        for i in range(0,len(tick_data)-2):
            assymetric_wings = 0
            
            #check if are symmetric wings
            diff_wings = tick_data[i].strike - (2 * tick_data[i + 1].strike) + tick_data[i + 2].strike
            
            wing_1_price = tick_data[i].ask
            wing_2_price = tick_data[i + 1].bid
            wing_3_price = tick_data[i + 2].ask
            if float(wing_1_price) == 0 or float(wing_2_price) == 0 or float(wing_3_price) == 0:
                continue
            
            cost =  wing_1_price - (2 * wing_2_price) + wing_3_price
            
            max_profit = round((tick_data[i + 1].strike - tick_data[i].strike) - cost,2)
            stock_price = float(tick_data[i].stock_price)
            percent_to_max_profit = round(((tick_data[i + 1].strike - stock_price) / stock_price)*100,2)
            max_loss = cost
            
            if diff_wings > 0 and show_broken_wings == False:
                continue
            else:
                max_loss = cost
                
            if cost < cost_limit:
                butterfly_symbols = '{}: {}, {}: {}, {}:{} '.format(tick_data[i].option_name
                                                    , round(wing_1_price,2)
                                                    , tick_data[i + 1].option_name
                                                    , round(wing_2_price,2)
                                                    , tick_data[i + 2].option_name
                                                    , round(wing_3_price,2))            
                model_return.append(
                    {
                    'BUTTERFLY': butterfly_symbols
                    , "COST": cost             
                    , "MAX_PROFIT": max_profit
                    , "MAX_LOSS": max_loss                 
                    , "DIFF_BETWEEN_WINGS": diff_wings
                    , "PERCENT_2_MAX_PAYOFF":percent_to_max_profit
                    })

        return model_return
    

    def update_quotes_from_database(self):
        due_dates = db.session.query(db.PETR4.due_date).distinct().filter(db.PETR4.due_date > datetime.datetime.today()).limit(5)
        due_dates = list(due_dates)

        month_deadline = due_dates[0].due_date
        next_month_dealine = due_dates[1].due_date
        after_next_month_dealine = due_dates[2].due_date
        long_due = due_dates[3].due_date

        this_month = datetime.datetime.today().date()
        diff_betwen_dates = month_deadline - this_month

        if diff_betwen_dates.days < 5:
            month_deadline = next_month_dealine
            next_month_dealine = after_next_month_dealine
            after_next_month_dealine = long_due

        last_date = db.session.query(db.PETR4_OPTIONS).filter(db.PETR4_OPTIONS.due_date == month_deadline).order_by(desc(db.PETR4_OPTIONS.updated_at)).first()
        month_last_ticks = db.session.query(db.PETR4_OPTIONS).filter(db.PETR4_OPTIONS.updated_at == last_date.updated_at, db.PETR4_OPTIONS.due_date == month_deadline).order_by(db.PETR4_OPTIONS.strike).all()
        next_month_last_ticks = db.session.query(db.PETR4_OPTIONS).filter(db.PETR4_OPTIONS.updated_at == last_date.updated_at, db.PETR4_OPTIONS.due_date == next_month_dealine).order_by(db.PETR4_OPTIONS.strike).all()
        after_next_month_last_ticks = db.session.query(db.PETR4_OPTIONS).filter(db.PETR4_OPTIONS.updated_at == last_date.updated_at, db.PETR4_OPTIONS.due_date == after_next_month_dealine).order_by(db.PETR4_OPTIONS.strike).all()
        
        #for tick in month_last_ticks:
        #   print(tick.updated_at, tick.timestamp_option, tick.option_name, tick.strike, tick.deal_type_zone, tick.stock_price, tick.bid, tick.ask, tick.last_tick)        
        
        return [month_last_ticks,next_month_last_ticks,after_next_month_last_ticks]
        
    def butterfly(self, cost_limit = 1, show_broken_wings = False, period = Option_Due.This_Month, mode=ButterFly_Mode.Offline):
        updated_ticks = self.update_quotes_from_database()
        ticks_to_process = 0

        if period == Option_Due.This_Month:
            ticks_to_process = updated_ticks[0]

        if period == Option_Due.Next_Month:
            ticks_to_process = updated_ticks[1]

        if period == Option_Due.After_Month:
            ticks_to_process = updated_ticks[2]
        
        if mode == ButterFly_Mode.Offline:
            return self.check_butterfly_database(ticks_to_process,cost_limit = cost_limit, show_broken_wings = show_broken_wings)

        if mode == ButterFly_Mode.Real_Time:
            return self.check_butterfly_realtime(ticks_to_process,cost_limit = cost_limit, show_broken_wings = show_broken_wings)