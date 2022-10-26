#from bmtk.analyzer.compartment import plot_traces
#_ = plot_traces(config_file='simulation_config.ccl.json', node_ids=[0,1,2,3,4], report_name='v_report')

import pdb
import h5py
import json
import numpy as np
import pandas 
import matplotlib.pyplot as plt

config_location = 'simulation_config.ccl.json'
trace_location = 'output/v_report.h5'

print("loading " + trace_location)
f = h5py.File(trace_location)

with open(config_location, mode='r') as cf:
    config = json.load(cf)

dt = config['run']['dt']

i_inj_nA = config['inputs']['cclamp']['amp']
i_inj_start = config['inputs']['cclamp']['delay']
i_inj_dur = config['inputs']['cclamp']['duration']

cells = [
    {'id':0,'name':'PN_A'},
    {'id':1,'name':'PN_C'},
    {'id':2,'name':'PV'},
    {'id':3,'name':'SOM'},
    {'id':4,'name':'CR'}   
]

traces = np.array(f['report']['BLA']['data']).T
ms = np.array([i for i in range(len(traces[0]))]) * dt

inj = np.zeros(len(traces[0]))
inj_range = np.array([i for i in range(int(i_inj_start/dt),int(i_inj_dur/dt))])
inj_range = inj_range[(inj_range < len(ms))]
inj[inj_range] = i_inj_nA * 1000


for cell in cells:
    cell_id = cell['id']

    trace = traces[cell_id]
    ms = np.array([i for i in range(len(trace))]) * dt

    # Creating plot with dataset_1
    fig, ax1 = plt.subplots()
    
    color = 'tab:red'
    ax1.set_xlabel('Time (ms)')
    ax1.set_ylabel('Voltage (mV)', color = color)
    ax1.plot(ms, trace, color = color)
    ax1.tick_params(axis ='y', labelcolor = color)
    ax1.set_ylim([-100, 30]) 
    # Adding Twin Axes to plot using dataset_2
    ax2 = ax1.twinx()
    
    color = 'tab:green'
    ax2.set_ylabel('Current (nA)', color = color)
    ax2.plot(ms, inj, color = color)
    ax2.tick_params(axis ='y', labelcolor = color)
    ax2.set_ylim([0, 1000])

    # Adding title
    plt.title(cell['name'], fontweight ="bold")    
    f_name = cell['name'] + '_inj.png'
    print("saving " + f_name)
    plt.savefig(f_name, bbox_inches='tight')
    #plt.show()

#trace_df = pd.DataFrame({'node_ids':f['spikes']['BLA']['node_ids'],'timestamps':f['spikes']['BLA']['timestamps']})
