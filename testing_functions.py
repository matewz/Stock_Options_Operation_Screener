import options_estrategies as opt_est
from options_estrategies import Option_Due, InformationType
import models as model

estrategies = opt_est.options_estrategies(model, model.PETR4, model.PETR4_OPTIONS)


def testing_anakha13_operations():
    returned_anakha13_operations = estrategies.anakha13_spiral(mode=InformationType.Offline)
    print(returned_anakha13_operations)

def testing_thl_operations():
    returned_thl_operations = estrategies.thl_operation(mode=InformationType.Offline)
    print(returned_thl_operations['thl'])
    print(returned_thl_operations['thl_next_month'])
    print(returned_thl_operations['thl_calendar'])

def testing_tax_operation():
    returned_tax_operation = estrategies.tax_operation()
    print(returned_tax_operation)

def testing_ratio_between_strikes_statistic_realtime_compare():
    returned_ratio_compare = estrategies.ratio_between_strikes_statistic_realtime_compare()
    print(returned_ratio_compare)

def testing_ratio_between_strikes_offline():
    ratio_returned = estrategies.ratio_between_strikes(just_last_update=True, period=Option_Due.This_Month, mode=InformationType.Offline)
    print(ratio_returned)

def testing_ratio_between_strikes_realtime():
    ratio_returned = estrategies.ratio_between_strikes(just_last_update=True, period=Option_Due.This_Month, mode=InformationType.Real_Time)
    print(ratio_returned)

def testing_butterfly_offline_for_this_month():  
    butterfly = estrategies.butterfly(0.05,False,Option_Due.This_Month, InformationType.Offline)
    print(butterfly)

def testing_butterfly_realtime_for_this_month():
    butterfly = estrategies.butterfly(0.05,False,Option_Due.This_Month, InformationType.Real_Time)
    print(butterfly)


testing_anakha13_operations()
testing_thl_operations()
testing_tax_operation()
testing_ratio_between_strikes_statistic_realtime_compare()
testing_ratio_between_strikes_offline()
testing_ratio_between_strikes_realtime()
testing_butterfly_offline_for_this_month()
testing_butterfly_realtime_for_this_month()