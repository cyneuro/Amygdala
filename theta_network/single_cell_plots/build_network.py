import numpy as np
from bmtk.builder.auxi.node_params import xiter_random
from bmtk.utils.sim_setup import build_env_bionet
from bmtk.builder import NetworkBuilder
from bmtk.builder.auxi.node_params import positions_cuboid, positions_list, xiter_random
import math
import random
import os, sys

network_dir = 'network'
components_dir = './components'
syn_dir='./components/synaptic_models'
t_sim = 500
dt = 0.05

#Number of cells in each population
numPN_A = 1
numPN_C = 1
numPV = 1
numSOM = 1
numCR = 1

min_conn_dist = 0.0
max_conn_dist = 300.0 #300.0 #9999.9# Distance constraint for all cells
net_size = 1000#um

num_cells = numPN_A + numPN_C + numPV + numSOM + numCR #Only used to populate an overall position list

# Create the possible x, y, z coordinates
x_start,  x_end = 0+max_conn_dist, net_size+max_conn_dist
y_start,  y_end = 0+max_conn_dist, net_size+max_conn_dist
z_start,  z_end = 0+max_conn_dist, net_size+max_conn_dist

pos_list = np.random.rand(num_cells, 3)
pos_list[: , 0] = pos_list[: , 0]*(x_end - x_start) + x_start
pos_list[: , 1] = pos_list[: , 1]*(y_end - y_start) + y_start
pos_list[: , 2] = pos_list[: , 2]*(z_end - z_start) + z_start


networks = {} #Place to store NetworkBuilder objects referenced by name
network_definitions = [
    {
        'network_name': 'BLA',
        'cells': [
            {   # Pyramidal Cells - Type A
                'N': numPN_A,
                'pop_name': 'PyrA',
                'a_name': 'PN',
                'model_type': 'biophysical',
                'model_template': 'hoc:Cell_Af'
            },
            {   # Pyramidal Cells - Type C
                'N': numPN_C,
                'pop_name': 'PyrC',
                'a_name': 'PN',
                'model_type': 'biophysical',
                'model_template': 'hoc:Cell_Cf'
            },
            {   # Interneuron - fast spiking PV
                'N': numPV,
                'pop_name': 'PV',
                'a_name': 'PV',
                'model_type': 'biophysical',
                'model_template': 'hoc:InterneuronCellf'
            },
            {   # Interneuron - SOM Cell
                'N': numSOM,
                'pop_name': 'SOM',
                'a_name': 'SOM',
                'model_type': 'biophysical',
                'model_template': 'hoc:SOM_Cell'
            },
            {   # Interneuron - CR Cell
                'N': numCR,
                'pop_name': 'CR',
                'a_name': 'CR',
                'model_type': 'biophysical',
                'model_template': 'hoc:CR_Cell'
            }
        ] # End cells
    }, # End BLA
]
##########################################################################
###############################  BUILD  ##################################
def build_networks(network_definitions: list) -> dict:
    # network_definitions should be a list of dictionaries eg:[{}]
    # Keys should include an arbitrary 'network_name', a positions_list (if any),
    # And 'cells'. 'cells' should contain a list of dictionaries, and the dictionary
    # should corrospond with any valid input for BMTK's NetworkBuilder.add_nodes method
    # A dictionary of NetworkBuilder BMTK objects will be returned, reference by individual network_name
    networks = {}

    for net_def in network_definitions:
        network_name = net_def['network_name']
        networks[network_name] = NetworkBuilder(network_name)
        pos_list = net_def.get('positions_list', None)

        # Add cells to the network
        for cell in net_def['cells']:
            num_cells = cell['N']
            extra_kwargs = {}
            if pos_list is not None:
                inds = np.random.choice(np.arange(0, np.size(pos_list, 0)), num_cells, replace=False)
                pos = pos_list[inds, :]
                # Get rid of coordinates already used
                pos_list = np.delete(pos_list, inds, 0)
                extra_kwargs['positions'] = positions_list(positions=pos)

            networks[network_name].add_nodes(**cell, **extra_kwargs)

    return networks

def save_networks(networks, network_dir):
    # Remove the existing network_dir directory
    for f in os.listdir(network_dir):
        os.remove(os.path.join(network_dir, f))

    # Run through each network and save their nodes/edges
    for i, (network_name, network) in enumerate(networks.items()):
        print('Building ' + network_name)
        network.build()
        network.save_nodes(output_dir=network_dir)
        network.save_edges(output_dir=network_dir)

networks = build_networks(network_definitions)
save_networks(networks, network_dir)

# Usually not necessary if you've already built your simulation config
build_env_bionet(base_dir='./',
	network_dir=network_dir,
	tstop=t_sim, dt = dt,
	report_vars = ['v'],
        v_init = -70.0,
        celsius = 31.0,
	components_dir=components_dir,
        config_file='simulation_config.json',
	compile_mechanisms=True)


