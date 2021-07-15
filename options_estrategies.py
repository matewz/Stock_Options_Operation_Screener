from sqlalchemy import extract, desc
import datetime
#import models as db
import time
import MetaTrader5 as mt5
import pandas as pd
from enum import Enum


class Option_Due(Enum):
    This_Month = 1
    Next_Month = 2
    After_Month = 3

class InformationType(Enum):
    Real_Time = 1
    Offline = 2

    
class options_estrategies():

    if not mt5.initialize():
        print("initialize() failed")
        mt5.shutdown()
    
    stock_class = ''
    stock_class_OPTIONS = ''
    model = None

    def __init__(self, model, stock_class, stock_class_OPTIONS):
        self.stock_class = stock_class
        self.stock_class_OPTIONS = stock_class_OPTIONS
        self.model = model

    def get_realtime_tick(self, symb):
        return { "timestamp": datetime.datetime.utcfromtimestamp(mt5.symbol_info_tick(symb).time).strftime('%Y-%m-%d %H:%M:%S'), "last": mt5.symbol_info_tick(symb).last,  "bid": mt5.symbol_info_tick(symb).bid , "ask": mt5.symbol_info_tick(symb).ask }

    def update_quote_realtime(self, ticks):
        updated_ticks = ticks
        for tick_count in range(0,len(updated_ticks)-1):
            for option in range(0,len(updated_ticks[tick_count])):
                symbol_data = self.get_realtime_tick(updated_ticks[tick_count][option].option_name)
                updated_ticks[tick_count][option].bid = symbol_data['bid']
                updated_ticks[tick_count][option].ask = symbol_data['ask']
                updated_ticks[tick_count][option].last_tick =symbol_data['last']
                updated_ticks[tick_count][option].timestamp_option = symbol_data['timestamp']
        return updated_ticks 

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
    

    def update_quotes(self,just_last_update = True, mode=InformationType.Offline):
        # You can just get get_real_time_ticks if use last_update == true
        
        due_dates = self.model.session.query(self.stock_class.due_date).distinct().filter(self.stock_class.due_date > datetime.datetime.today()).limit(5)
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

        last_date = self.model.session.query(self.stock_class_OPTIONS).filter(self.stock_class_OPTIONS.due_date == month_deadline).order_by(desc(self.stock_class_OPTIONS.updated_at)).first()
        
        if just_last_update == True:
            month_last_ticks = self.model.session.query(self.stock_class_OPTIONS).filter(self.stock_class_OPTIONS.updated_at == last_date.updated_at, self.stock_class_OPTIONS.due_date == month_deadline).order_by(self.stock_class_OPTIONS.strike).all()
            next_month_last_ticks = self.model.session.query(self.stock_class_OPTIONS).filter(self.stock_class_OPTIONS.updated_at == last_date.updated_at, self.stock_class_OPTIONS.due_date == next_month_dealine).order_by(self.stock_class_OPTIONS.strike).all()
            after_next_month_last_ticks = self.model.session.query(self.stock_class_OPTIONS).filter(self.stock_class_OPTIONS.updated_at == last_date.updated_at, self.stock_class_OPTIONS.due_date == after_next_month_dealine).order_by(self.stock_class_OPTIONS.strike).all()
        else:
            month_last_ticks = self.model.session.query(self.stock_class_OPTIONS).filter(self.stock_class_OPTIONS.due_date == month_deadline).order_by(self.stock_class_OPTIONS.updated_at,self.stock_class_OPTIONS.strike).all()
            next_month_last_ticks = self.model.session.query(self.stock_class_OPTIONS).filter(self.stock_class_OPTIONS.due_date == next_month_dealine).order_by(self.stock_class_OPTIONS.updated_at,self.stock_class_OPTIONS.strike).all()
            after_next_month_last_ticks = self.model.session.query(self.stock_class_OPTIONS).filter(self.stock_class_OPTIONS.due_date == after_next_month_dealine).order_by(self.stock_class_OPTIONS.updated_at,self.stock_class_OPTIONS.strike).all()
            
            #for tick in month_last_ticks:
            #   print(tick.updated_at, tick.timestamp_option, tick.option_name, tick.strike, tick.deal_type_zone, tick.stock_price, tick.bid, tick.ask, tick.last_tick)        
        
        ticks_to_return = [month_last_ticks,next_month_last_ticks,after_next_month_last_ticks]

        if just_last_update == True and mode == InformationType.Real_Time:
            ticks_to_return = self.update_quote_realtime(ticks_to_return)

        return ticks_to_return

    def butterfly(self, cost_limit = 1, show_broken_wings = False, period = Option_Due.This_Month, mode=InformationType.Offline):
        updated_ticks = self.update_quotes()
        ticks_to_process = 0

        if period == Option_Due.This_Month:
            ticks_to_process = updated_ticks[0]

        if period == Option_Due.Next_Month:
            ticks_to_process = updated_ticks[1]

        if period == Option_Due.After_Month:
            ticks_to_process = updated_ticks[2]
        
        if mode == InformationType.Offline:
            return self.check_butterfly_database(ticks_to_process,cost_limit = cost_limit, show_broken_wings = show_broken_wings)

        if mode == InformationType.Real_Time:
            return self.check_butterfly_realtime(ticks_to_process,cost_limit = cost_limit, show_broken_wings = show_broken_wings)

    def convert_dict_from_update_ticks_to_dataframe(self,tick_data):
        df_tick_data = pd.DataFrame.from_dict(tick_data)
        df_tick_data = df_tick_data.drop(columns=['_sa_instance_state','timestamp_option','days_to_due_date'])
        df_tick_data['ratio'] = df_tick_data['last_tick'] - df_tick_data['last_tick'].shift(1)
        df_tick_data = df_tick_data[['option_name', 'strike', 'bid', 'ask', 'last_tick','ratio','stock_price','deal_type_zone','updated_at']]      
        return df_tick_data

    def ratio_between_strikes(self, just_last_update= True, mode=InformationType.Offline, period = Option_Due.This_Month):

        updated_ticks = self.update_quotes(just_last_update=just_last_update,mode=mode)

        if period == Option_Due.This_Month:
            ticks_to_process = updated_ticks[0]

        if period == Option_Due.Next_Month:
            ticks_to_process = updated_ticks[1]

        if period == Option_Due.After_Month:
            ticks_to_process = updated_ticks[2]

        options = []
        for i in ticks_to_process:
            options.append(i.__dict__)

        return_dataframe = self.convert_dict_from_update_ticks_to_dataframe(options)

        return return_dataframe

    def ratio_between_strikes_statistic_realtime_compare(self):
        df_options_history  = self.ratio_between_strikes(False)

        ratio_statistic_finder = df_options_history[['updated_at','option_name','ratio']]
        ratio_statistic_finder.set_index('updated_at')
        ratio_statistic_finder = ratio_statistic_finder.pivot(index='updated_at', columns='option_name', values='ratio')
        ratio_statistic_finder = ratio_statistic_finder.dropna(axis=True)

        ratio_statistic_data = {}
        for (column, value) in ratio_statistic_finder.iteritems():
            ratio_statistic_data.update({ column: { "Mean": ratio_statistic_finder[column].mean(), "StdDev": ratio_statistic_finder[column].std(), "2xStdDev": (ratio_statistic_finder[column].std()*2)  }}) 

        ratio_statistic_dataframe = pd.DataFrame.from_dict(ratio_statistic_data)
        ratio_statistic_dataframe = ratio_statistic_dataframe.transpose()

        updated_ticks = self.update_quotes(just_last_update=True,mode=InformationType.Real_Time)
        ticks_to_process = updated_ticks[0]
        options_updated = []
        for i in ticks_to_process:
            options_updated.append(i.__dict__)

        df_options_updated = self.convert_dict_from_update_ticks_to_dataframe(options_updated)
        df_options_updated.reset_index()
        df_options_updated = df_options_updated.set_index('option_name')
        df_options_updated = pd.merge(df_options_updated, ratio_statistic_dataframe, left_index=True, right_index=True)

        df_options_updated['above_mean'] = abs(df_options_updated['ratio']) > abs(df_options_updated['Mean'])
        df_options_updated['above_2x_std_dev'] = abs(df_options_updated['ratio']) > abs(abs(df_options_updated['Mean']) + df_options_updated['2xStdDev'])
        return df_options_updated