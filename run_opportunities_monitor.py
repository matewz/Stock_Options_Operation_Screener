import options_estrategies as opt_est
from options_estrategies import Option_Due, InformationType
import models as model
import winsound
import time
import datetime
import pandas as pd

estrategies = opt_est.options_estrategies(model, model.PETR4, model.PETR4_OPTIONS)

last_warnings = []
alarme_to_remove = []

def check_exists_alarm(operation, option_name, time_expiration = 4):
    for i in range(0,len(last_warnings)):
        if last_warnings[i]['timestamp'] < (datetime.datetime.now() - datetime.timedelta(minutes=time_expiration)):
            alarme_to_remove.append(last_warnings[i])

    for i in range(0,len(alarme_to_remove)):
        last_warnings.remove(last_warnings[i])
    
    alarme_to_remove.clear()

    for i in range(0,len(last_warnings)):
        if last_warnings[i]['operation'] == str(operation) and last_warnings[i]['option_name'] == str(option_name):
            return True
        
    return False
    
    
def add_alarm(operation, option_name):
    warning = dict(operation=str(operation), option_name=str(option_name), timestamp=datetime.datetime.now())
    last_warnings.append(warning)


def ratio_compare():
    returned_ratio_compare = estrategies.ratio_between_strikes_statistic_realtime_compare()
    returned_ratio = returned_ratio_compare.copy()
    returned_ratio = returned_ratio.reset_index()
    ratio_deviation_high = returned_ratio[returned_ratio['above_2x_std_dev'] == True]

    return_operation = []

    for index, row in ratio_deviation_high.iterrows():
        if index > 0:
            data_ratio = returned_ratio[index-1:index+ 1].copy()
            data_ratio.insert(0, 'operation', ['C','V'])
            return_operation.append(data_ratio)

    return_operation
    if len(return_operation) > 0:
        if check_exists_alarm('RATIO_COMPARE',return_operation) == False:
            AvisoSonoro(500)
            add_alarm('RATIO_COMPARE',return_operation)
        
            print("---------------------------------- 2x dev ---------------------")
            print(return_operation)
            print("---------------------------------- 2x dev ---------------------")

def thl_compare():
    returned_thl_operations = estrategies.thl_operation(mode=InformationType.Real_Time)
    
    comparison_this_month = returned_thl_operations['thl']
    comparison_next_month = returned_thl_operations['thl_next_month']
    comparison_calendar = returned_thl_operations['thl_calendar']

    good_operation_THL = comparison_this_month[comparison_this_month['thl_percent_of_strike'] < 1.5]
    good_operation_THL_next_month = comparison_next_month[comparison_next_month['thl_percent_of_strike'] < 1.5]
    good_operation_calendar = comparison_calendar[comparison_calendar['thl_percent_of_strike'] < 1.5]

    if len(good_operation_THL.index) > 0:
        if check_exists_alarm('THL',good_operation_THL) == False:
            AvisoSonoro(400)
            add_alarm('THL',good_operation_THL)

            print("---------------------------------- THL ---------------------")
            print(good_operation_THL)
            print("---------------------------------- THL ---------------------")
            
    if len(good_operation_THL_next_month.index) > 0:
        if check_exists_alarm('THL',good_operation_THL_next_month) == False:
            AvisoSonoro(400)
            add_alarm('THL',good_operation_THL_next_month)

            print("---------------------------------- THL NEXT MONTH ---------------------")
            print(good_operation_THL_next_month)
            print("---------------------------------- THL NEXT MONTH ---------------------")
        

    if len(good_operation_calendar.index) > 0:
        if check_exists_alarm('THL',good_operation_calendar) == False:
            AvisoSonoro(400)
            add_alarm('THL',good_operation_calendar)

            print("---------------------------------- THL CALENDAR ---------------------")
            print(good_operation_THL_next_month)
            print("---------------------------------- THL CALENDAR ---------------------")        


def butterfly_compare():

    returned_butterfly_operations = estrategies.butterfly(cost_limit = 0.03, show_broken_wings = False, period = Option_Due.This_Month, mode=InformationType.Real_Time)
    if len(returned_butterfly_operations) > 0:
        df_butterfly_offline = pd.DataFrame.from_dict(returned_butterfly_operations)
        #print(df_butterfly_offline)
        df_butterfly_offline = df_butterfly_offline [['BUTTERFLY','COST','MAX_VOLUME','PERCENT_2_MAX_PAYOFF']]

        if check_exists_alarm('BUTTERFLY',df_butterfly_offline) == False:
            AvisoSonoro(300)
            add_alarm('BUTTERFLY',df_butterfly_offline)

            print("---------------------------------- BUTTERFLY ---------------------")
            print(df_butterfly_offline)
            print("---------------------------------- returned_butterfly_operations ---------------------")        




def AvisoSonoro(freq):
    duration = 500  # milliseconds
    for i in range(0,5):
        winsound.Beep(freq, duration)

while 1:
    butterfly_compare()
    ratio_compare()
    thl_compare()


    time.sleep(1)