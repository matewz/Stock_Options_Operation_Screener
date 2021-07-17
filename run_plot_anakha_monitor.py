import options_estrategies as opt_est
from options_estrategies import Option_Due, InformationType
import models as model

from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt

estrategies = opt_est.options_estrategies(model, model.PETR4, model.PETR4_OPTIONS)


fig, anakhaChart = plt.subplots(1)

def anakha_chart(i):

    df_tick_data = estrategies.anakha13_spiral(mode=InformationType.Real_Time)
    plot_dataframe = df_tick_data
    plot_dataframe = plot_dataframe[1:len(plot_dataframe)-1]
    unique_options = plot_dataframe['option_name'].unique()
    options_name = list(unique_options)

    #anakhaChart.plot(options_name, options_name["anakha_1.3"], color='skyblue')
    #ax = plot_dataframe.plot(x="option_name", y=["anakha_1.3"],figsize=(15,7),ylim=(-0.60,0.60),x_compat=True)

    anakhaChart.cla()
    unique_options = plot_dataframe['option_name'].unique()
    options_name = list(unique_options)
    anakhaChart.plot(options_name, plot_dataframe["anakha_1.3"], color='skyblue')
    anakhaChart.grid()
    plt.ylim(-0.60,0.60)
    plt.xticks(range(0,len(options_name)), options_name)


ani = FuncAnimation(plt.gcf(), anakha_chart, 10000)
plt.show()


