import options_estrategies as opt_est
from options_estrategies import Option_Due, InformationType
import models as model
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
import numpy as np
import time

estrategies = opt_est.options_estrategies(model, model.PETR4, model.PETR4_OPTIONS)
df_tick_data = estrategies.anakha13_spiral(just_last_update=False, mode=InformationType.Offline)

anakha_param = 'anakha_1.2'

df_tick_data = df_tick_data[(df_tick_data[anakha_param + '_pct_change'] < 0.20) & (df_tick_data[anakha_param + '_pct_change'] > -0.60)]
df_tick_data = df_tick_data.sort_values(by=anakha_param + '_pct_change', ascending=False).copy()

datetime_ticks = df_tick_data 
datetime_ticks = datetime_ticks.set_index('updated_at')
datetime_ticks = datetime_ticks.sort_values(by='updated_at')

unique_options = datetime_ticks['option_name'].unique()
upload_datetime = datetime_ticks.index.unique()


# plt.ion()
# for i in range(50):
#     y = np.random.random([10,1])
#     plt.plot(y)
#     plt.draw()
#     plt.pause(0.0001)
#     plt.clf()

    
# You probably won't need this if you're embedding things in a tkinter plot...
plt.ion()

for itm in upload_datetime:
    plot_dataframe = df_tick_data[(df_tick_data['updated_at'] == itm)]
    plot_dataframe = plot_dataframe.sort_values(by='strike')

    title = plot_dataframe.iloc[0]['updated_at']
    plot_dataframe = plot_dataframe[1:len(plot_dataframe)-1]
    
    unique_options = plot_dataframe['option_name'].unique()
    options_name = list(unique_options)
    y = list(plot_dataframe[anakha_param])

    plt.plot(options_name,y, color='skyblue')
    plt.ylim(-0.60,0.60)
    plt.xticks(range(0,len(options_name)), options_name, rotation='vertical')
    plt.title(title)
    plt.draw()
    plt.pause(1)
    plt.clf()

# x = np.linspace(0, 6*np.pi, 100)
# y = np.sin(x)

# # You probably won't need this if you're embedding things in a tkinter plot...
# plt.ion()

# fig = plt.figure()
# ax = fig.add_subplot(111)
# line1, = ax.plot(x, y, 'r-') # Returns a tuple of line objects, thus the comma

# for phase in np.linspace(0, 10*np.pi, 500):
#     line1.set_ydata(np.sin(x + phase))
#     fig.canvas.draw()
#     fig.canvas.flush_events()

    



# last_updated = ''

# fig, anakhaChart = plt.subplots(1)

# upload_datetime = df_tick_data.index.unique()
# unique_options = df_tick_data['option_name'].unique()
# upload_item = 0

# def anakha_chart(i):
    
#     # run this file to get information from database and make animated chart to understand the option behavior
#     datetime_ticks = df_tick_data[(df_tick_data['updated_at'] > '2021-07-15 00:00:01') & (df_tick_data['updated_at'] <'2021-07-15 23:59:59')]

#     upload_item = upload_item + 1 
#     return upload_item
#     # df_tick_data = estrategies.anakha13_spiral(mode=InformationType.Real_Time)
#     # plot_dataframe = df_tick_data
#     # plot_dataframe = plot_dataframe[1:len(plot_dataframe)-1]
#     # unique_options = plot_dataframe['option_name'].unique()
#     # options_name = list(unique_options)

#     # #anakhaChart.plot(options_name, options_name["anakha_1.3"], color='skyblue')
#     # #ax = plot_dataframe.plot(x="option_name", y=["anakha_1.3"],figsize=(15,7),ylim=(-0.60,0.60),x_compat=True)

#     # anakhaChart.cla()
#     # unique_options = plot_dataframe['option_name'].unique()
#     # options_name = list(unique_options)
#     # anakhaChart.plot(options_name, plot_dataframe["anakha_1.3"], color='skyblue')
#     # anakhaChart.grid()
#     # plt.ylim(-0.60,0.60)
#     # plt.xticks(range(0,len(options_name)), options_name)


# ani = FuncAnimation(plt.gcf(), anakha_chart, 10000)
# plt.show()
