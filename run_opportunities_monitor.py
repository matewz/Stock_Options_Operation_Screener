import options_estrategies as opt_est
from options_estrategies import Option_Due, InformationType
import models as model
import winsound
import time

estrategies = opt_est.options_estrategies(model, model.PETR4, model.PETR4_OPTIONS)

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
        AvisoSonoro(500)
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
        AvisoSonoro(400)
        print("---------------------------------- THL ---------------------")
        print(good_operation_THL)
        print("---------------------------------- THL ---------------------")
        
    if len(good_operation_THL_next_month.index) > 0:
        AvisoSonoro(400)
        print("---------------------------------- THL NEXT MONTH ---------------------")
        print(good_operation_THL_next_month)
        print("---------------------------------- THL NEXT MONTH ---------------------")
        
        print(good_operation_THL_next_month)

    if len(good_operation_calendar.index) > 0:
        AvisoSonoro(400)
        print("---------------------------------- THL CALENDAR ---------------------")
        print(good_operation_THL_next_month)
        print("---------------------------------- THL CALENDAR ---------------------")        
        print(good_operation_calendar) 

def AvisoSonoro(freq):
    duration = 200  # milliseconds
    for i in range(0,1):
        winsound.Beep(freq, duration)

while 1:
    ratio_compare()
    thl_compare()
    time.sleep(1)