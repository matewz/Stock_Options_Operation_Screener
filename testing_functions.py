from sqlalchemy.sql.functions import mode
import options_estrategies as opt_est
from options_estrategies import Option_Due, ButterFly_Mode
import models as model

def testing_butterfly_offline_for_this_month():
    estrategies = opt_est.options_estrategies(model, model.PETR4, model.PETR4_OPTIONS)
    butterfly = estrategies.butterfly(0.05,False,Option_Due.This_Month, ButterFly_Mode.Offline)
    print(butterfly)

def testing_butterfly_realtime_for_this_month():
    estrategies = opt_est.options_estrategies(model, model.PETR4, model.PETR4_OPTIONS)
    butterfly = estrategies.butterfly(0.05,False,Option_Due.This_Month, ButterFly_Mode.Real_Time)
    print(butterfly)

testing_butterfly_offline_for_this_month()
testing_butterfly_realtime_for_this_month()