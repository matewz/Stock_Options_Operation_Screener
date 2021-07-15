import options_estrategies as opt_est
from options_estrategies import Option_Due, InformationType
import models as model
import winsound
import time

estrategies = opt_est.options_estrategies(model, model.PETR4, model.PETR4_OPTIONS)

def ratio_compare():
    returned_ratio_compare = estrategies.ratio_between_strikes_statistic_realtime_compare()
    print(returned_ratio_compare[returned_ratio_compare['above_mean'] == True])

    ratio_deviation_high = returned_ratio_compare[returned_ratio_compare['above_2x_std_dev'] == True]
    if len(ratio_deviation_high) > 0:
        AvisoSonoro(1500)
        print("---------------------------------- 2x dev ---------------------")
        print(ratio_deviation_high)
        print("---------------------------------- 2x dev ---------------------")


def AvisoSonoro(freq):
    duration = 400  # milliseconds
    for i in range(0,15):
        winsound.Beep(freq, duration)

while 1:
    ratio_compare()

    time.sleep(2)