from bmtk.builder import NetworkBuilder
from bmtk.builder.auxi.node_params import positions_list, xiter_random
from bmtk.utils.sim_setup import build_env_bionet
from amygdala_core import synapses
import os, sys
import warnings

from amygdala_core.builder import build_networks, build_edges, save_networks
from amygdala_core.connectors import *

np.random.seed(123412)
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=DeprecationWarning)
network_dir = 'network'
components_dir = '../components'
t_sim = 15000.0
dt = 0.05
scale = 4

min_conn_dist = 0.0
max_conn_dist = 9999  # 300.0 #9999.9# Distance constraint for all cells

# When enabled, a shell of virtual cells will be created around the core network.
edge_effects = False
net_size = 400  # um

# Number of cells in each population
numPN_A = 569
numPN_C = 231
numPV = 93
numSOM = 107
numVIP = 107
numCR = 0

if os.path.isdir('network') == False:
    os.makedirs('network')
# Scale the number of cells in each population
numPN_A = numPN_A * scale  # 640 * scale #4114#15930
numPN_C = numPN_C * scale  # 260 * scale #4115#6210
numPV = numPV * scale  # 100 * scale #854#4860
numSOM = numSOM * scale  # 42 * scale
numCR = numCR * scale  # 42 * scale
numVIP = numVIP * scale
num_cells = numPN_A + numPN_C + numPV + numSOM + numVIP  # Only used to populate an overall position list

# Create the possible x,y,z coordinates
x_start, x_end = 0 + max_conn_dist, net_size + max_conn_dist
y_start, y_end = 0 + max_conn_dist, net_size + max_conn_dist
z_start, z_end = 0 + max_conn_dist, net_size + max_conn_dist

if not edge_effects:
    x_start, x_end = 0, net_size
    y_start, y_end = 0, net_size
    z_start, z_end = 0, net_size

pos_list = np.random.rand(num_cells, 3)
pos_list[:, 0] = pos_list[:, 0] * (x_end - x_start) + x_start
pos_list[:, 1] = pos_list[:, 1] * (y_end - y_start) + y_start
pos_list[:, 2] = pos_list[:, 2] * (z_end - z_start) + z_start

networks = {}  # Place to store NetworkBuilder objects referenced by name
network_definitions = [
    {
        'network_name': 'BLA',
        'positions_list': pos_list,
        'cells': [
            {  # Pyramidal Cells - Type A
                'N': numPN_A,
                'pop_name': 'PyrA',
                'a_name': 'PN',
                'rotation_angle_zaxis': xiter_random(N=numPN_A, min_x=0.0, max_x=2 * np.pi),
                'rotation_angle_yaxis': xiter_random(N=numPN_A, min_x=0.0, max_x=2 * np.pi),
                'model_type': 'biophysical',
                'model_template': 'hoc:PN_A'
            },
            {  # Pyramidal Cells - Type C
                'N': numPN_C,
                'pop_name': 'PyrC',
                'a_name': 'PN',
                'rotation_angle_zaxis': xiter_random(N=numPN_C, min_x=0.0, max_x=2 * np.pi),
                'rotation_angle_yaxis': xiter_random(N=numPN_C, min_x=0.0, max_x=2 * np.pi),
                'model_type': 'biophysical',
                'model_template': 'hoc:PN_C'
            },
            {  # Interneuron - fast spiking PV
                'N': numPV,
                'pop_name': 'PV',
                'a_name': 'PV',
                'rotation_angle_zaxis': xiter_random(N=numPV, min_x=0.0, max_x=2 * np.pi),
                'rotation_angle_yaxis': xiter_random(N=numPV, min_x=0.0, max_x=2 * np.pi),
                'model_type': 'biophysical',
                'model_template': 'hoc:InterneuronCellf'
            },
            {  # Interneuron - SOM Cell
                'N': numSOM,
                'pop_name': 'SOM',
                'a_name': 'SOM',
                'rotation_angle_zaxis': xiter_random(N=numSOM, min_x=0.0, max_x=2 * np.pi),
                'rotation_angle_yaxis': xiter_random(N=numSOM, min_x=0.0, max_x=2 * np.pi),
                'model_type': 'biophysical',
                'model_template': 'hoc:SOM_Cell'
            },
            {  # Interneuron - VIP Cell
                'N': numVIP,
                'pop_name': 'VIP',
                'a_name': 'VIP',
                'rotation_angle_zaxis': xiter_random(N=numVIP, min_x=0.0, max_x=2 * np.pi),
                'rotation_angle_yaxis': xiter_random(N=numVIP, min_x=0.0, max_x=2 * np.pi),
                'model_type': 'biophysical',
                'model_template': 'hoc:SOM_Cell'
            },

            # {   # Interneuron - CR Cell
            #    'N':numCR,
            #    'pop_name':'CR',
            #    'a_name':'CR',
            #    'rotation_angle_zaxis':xiter_random(N=numCR, min_x=0.0, max_x=2*np.pi),
            #    'rotation_angle_yaxis':xiter_random(N=numCR, min_x=0.0, max_x=2*np.pi),
            #    'model_type':'biophysical',
            #    'model_template':'hoc:CR_Cell'
            # }
        ]  # End cells
    },  # End BLA
    {
        # Thalamic PYR INPUTS
        'network_name': 'thalamus_pyr_A',
        'positions_list': None,
        'cells': [
            {
                'N': numPN_A,
                'pop_name': 'pyrA_inp',
                'pop_group': 'thalamus_pyrA',
                'model_type': 'virtual'
            }
        ]
    },
    {
            # Thalamic PYR INPUTS
            'network_name': 'thalamus_pyr_C',
            'positions_list': None,
            'cells': [
                {
                    'N': numPN_C,
                    'pop_name': 'pyrC_inp',
                    'pop_group': 'thalamus_pyrC',
                    'model_type': 'virtual'
                }
            ]
        },
    {
        # Thalamic PV INPUTS
        'network_name': 'thalamus_pv',
        'positions_list': None,
        'cells': [
            {
                'N': numPV,
                'pop_name': 'pv_inp',
                'pop_group': 'thalamus_pv',
                'model_type': 'virtual'
            }
        ]
    },
    {
        # Thalamic SOM INPUTS
        'network_name': 'thalamus_som',
        'positions_list': None,
        'cells': [
            {
                'N': numSOM,
                'pop_name': 'som_inp',
                'pop_group': 'thalamus_som',
                'model_type': 'virtual'
            }
        ]
    },
    {
        # Thalamic VIP INPUTS
        'network_name': 'thalamus_vip',
        'positions_list': None,
        'cells': [
            {
                'N': numVIP,
                'pop_name': 'vip_inp',
                'pop_group': 'thalamus_vip',
                'model_type': 'virtual'
            }
        ]
    },
    # {
    #    # Thalamic CR INPUTS
    #    'network_name':'thalamus_cr',
    #    'positions_list':None,
    #    'cells':[
    #        {
    #            'N':numCR,
    #            'pop_name':'cr_inp',
    #            'pop_group':'thalamus_cr',
    #            'model_type':'virtual'
    #        }
    #    ]
    # },
    {
        # Tone
        'network_name': 'tone',
        'positions_list': None,
        'cells': [
            {
                'N': 1,
                'pop_name': 'tone',
                'pop_group': 'tone',
                'model_type': 'virtual'
            }
        ]
    },
    {
        # Shock
        'network_name': 'shock',
        'positions_list': None,
        'cells': [
            {
                'N': 1,
                'pop_name': 'shock',
                'pop_group': 'shock',
                'model_type': 'virtual'
            }
        ]
    }
]

##########################################################################
############################  EDGE EFFECTS  ##############################

if edge_effects:  # When enabled, a shell of virtual cells will be created around the core network.

    # compute the core volume
    core_x, core_y, core_z = (x_end - x_start), (y_end - y_start), (z_end - z_start)
    core_volume = core_x * core_y * core_z

    # compute the outer shell volume. The absolute max_conn_dist will extend each dimension of the core by 2*max_conn_dist
    shell_x_start, shell_y_start, shell_z_start = x_start - max_conn_dist, x_start - max_conn_dist, z_start - max_conn_dist
    shell_x_end, shell_y_end, shell_z_end = x_end + max_conn_dist, y_end + max_conn_dist, z_end + max_conn_dist
    shell_x, shell_y, shell_z = (shell_x_end - shell_x_start), (shell_y_end - shell_y_start), (
                shell_z_end - shell_z_start)
    shell_volume = shell_x * shell_y * shell_z

    # Determine the size difference between core and shell
    shell_multiplier = (shell_volume / core_volume)

    # Increase the number of original cells based on the shell_multiplier
    virt_numPN_A = int(numPN_A * shell_multiplier)
    virt_numPN_C = int(numPN_C * shell_multiplier)
    virt_numPV = int(numPV * shell_multiplier)
    virt_numSOM = int(numSOM * shell_multiplier)
    virt_numCR = int(numCR * shell_multiplier)
    virt_num_cells = virt_numPN_A + virt_numPN_C + virt_numPV + virt_numSOM + virt_numCR

    # Create a positions list for each cell in the shell, this includes positions in the core
    virt_pos_list = np.random.rand(virt_num_cells, 3)
    virt_pos_list[:, 0] = virt_pos_list[:, 0] * (shell_x_end - shell_x_start) + shell_x_start
    virt_pos_list[:, 1] = virt_pos_list[:, 1] * (shell_y_end - shell_y_start) + shell_y_start
    virt_pos_list[:, 2] = virt_pos_list[:, 2] * (shell_z_end - shell_z_start) + shell_z_start

    # EXCLUDE POSITIONS IN THE CORE - We remove all virtual cells located in the core (accounting for no -1 on shell_multiplier)
    in_core = np.where(((virt_pos_list[:, 0] > x_start) & (virt_pos_list[:, 0] < x_end)) &
                       ((virt_pos_list[:, 1] > y_start) & (virt_pos_list[:, 1] < y_end)) &
                       ((virt_pos_list[:, 2] > z_start) & (virt_pos_list[:, 2] < z_end)))
    virt_pos_list = np.delete(virt_pos_list, in_core, 0)

    # Bring down the number of shell cells to create by scaling
    # This ensures we have enough positions in virt_pos_list for all of our cells
    # Old density multiplied by new number of cells
    new_virt_num_cells = len(virt_pos_list)
    virt_numPN_A = int(virt_numPN_A / virt_num_cells * new_virt_num_cells)
    virt_numPN_C = int(virt_numPN_C / virt_num_cells * new_virt_num_cells)
    virt_numPV = int(virt_numPV / virt_num_cells * new_virt_num_cells)
    virt_numSOM = int(virt_numSOM / virt_num_cells * new_virt_num_cells)
    virt_numCR = int(virt_numCR / virt_num_cells * new_virt_num_cells)
    virt_num_cells = virt_numPN_A + virt_numPN_C + virt_numPV + virt_numSOM + virt_numCR

    # This should always be true, virt_num_cells is now equal to a scaled down number
    # While new_virt_num_cells is the length of the available cells
    assert (virt_num_cells <= new_virt_num_cells)

    # This network should contain all the same properties as the original network, except
    # the cell should be virtual. For connectivity, you should name the cells the same as
    # the original network because connection rules defined later will require it
    shell_network = {
        'network_name': 'shell',
        'positions_list': virt_pos_list,
        'cells': [
            {  # Pyramidal Cells - Type A
                'N': virt_numPN_A,
                'pop_name': 'PyrA',
                'a_name': 'PN',
                'rotation_angle_zaxis': xiter_random(N=virt_numPN_A, min_x=0.0, max_x=2 * np.pi),
                'rotation_angle_yaxis': xiter_random(N=virt_numPN_A, min_x=0.0, max_x=2 * np.pi),
                'model_type': 'virtual'
            },
            {  # Pyramidal Cells - Type C
                'N': virt_numPN_C,
                'pop_name': 'PyrC',
                'a_name': 'PN',
                'rotation_angle_zaxis': xiter_random(N=virt_numPN_C, min_x=0.0, max_x=2 * np.pi),
                'rotation_angle_yaxis': xiter_random(N=virt_numPN_C, min_x=0.0, max_x=2 * np.pi),
                'model_type': 'virtual'
            },
            {  # Interneuron - fast spiking PV
                'N': virt_numPV,
                'pop_name': 'PV',
                'a_name': 'PV',
                'rotation_angle_zaxis': xiter_random(N=virt_numPV, min_x=0.0, max_x=2 * np.pi),
                'rotation_angle_yaxis': xiter_random(N=virt_numPV, min_x=0.0, max_x=2 * np.pi),
                'model_type': 'virtual'
            },
            {  # Interneuron - SOM Cell
                'N': virt_numSOM,
                'pop_name': 'SOM',
                'a_name': 'SOM',
                'rotation_angle_zaxis': xiter_random(N=virt_numSOM, min_x=0.0, max_x=2 * np.pi),
                'rotation_angle_yaxis': xiter_random(N=virt_numSOM, min_x=0.0, max_x=2 * np.pi),
                'model_type': 'virtual'
            }
            #{  # Interneuron - CR Cell
            #    'N': virt_numCR,
            #    'pop_name': 'CR',
            #    'a_name': 'CR',
            #    'rotation_angle_zaxis': xiter_random(N=virt_numCR, min_x=0.0, max_x=2 * np.pi),
            #    'rotation_angle_yaxis': xiter_random(N=virt_numCR, min_x=0.0, max_x=2 * np.pi),
            #    'model_type': 'virtual'
            #}
        ]
    }

    # Add the shell to our network definitions
    network_definitions.append(shell_network)

##########################################################################
##########################################################################

# Build and save our NetworkBuilder dictionary
networks = build_networks(network_definitions)

# A few connectors require a list for tracking synapses that are recurrent, declare them here
int2int_temp_list = []
uncoupled_bi_track = []
pyr_int_bi_list = []
PV2SOM_bi_list = []
VIP2SOM_bi_list = []

# Whole reason for restructuring network building lies here, by separating out the
# source and target params from the remaining parameters in NetworkBuilder's
# add_edges function we can reuse connectivity rules for the virtual shell
# or elsewhere
# [
#    {
#       'network':'network_name', # => The name of the network that these edges should be added to (networks['network_name'])
#       'edge': {
#                    'source': {},
#                    'target': {}
#               }, # should contain source and target only, any valid add_edges param works
#       'param': 'name_of_edge_parameter' # to be coupled with when add_edges is called
#       'add_properties': 'prop_name' # name of edge_add_properties for adding additional connection props, like delay
#    }
# ]

edge_definitions = [
    {  # Pyramidal to Pyramidal Connections
        'network': 'BLA',
        'edge': {
            'source': {'pop_name': ['PyrA', 'PyrC']},
            'target': {'pop_name': ['PyrA', 'PyrC']}
        },
        'param': 'PYR2PYR',
        'add_properties': 'syn_dist_delay_feng_section_default'
    },
    {  # PV to PV Uncoupled Unidirectional
        'network': 'BLA',
        'edge': {
            'source': {'pop_name': ['PV']},
            'target': {'pop_name': ['PV']}
        },
        'param': 'PV2PV',
        'add_properties': 'syn_dist_delay_feng_section_default'
    },
    {   # PV to PV Uncoupled Bidirectional Pair
        'network':'BLA',
        'edge': {
            'source':{'pop_name': ['PV']},
            'target':{'pop_name': ['PV']}
        },
        'param': 'PV2PV_bi_1',
        'add_properties': 'syn_dist_delay_feng_section_default'
    },
    {   # PV to PV Uncoupled Bidirectional Pair
        'network':'BLA',
        'edge': {
            'source':{'pop_name': ['PV']},
            'target':{'pop_name': ['PV']}
        },
        'param': 'PV2PV_bi_2',
        'add_properties': 'syn_dist_delay_feng_section_default'
    },
    {  # PV to PYR Unidirectional
        'network': 'BLA',
        'edge': {
            'source': {'pop_name': ['PV']},
            'target': {'pop_name': ['PyrA', 'PyrC']}
        },
        'param': 'PV2PYR',
        'add_properties': 'syn_dist_delay_feng_section_default'
    },
    {  # PYR to PV Bidirectional
        'network': 'BLA',
        'edge': {
            'source': {'pop_name': ['PyrA', 'PyrC']},
            'target': {'pop_name': ['PV']}
        },
        'param': 'PYR2PV',
        'add_properties': 'syn_dist_delay_feng_section_default'
    },
    {  # PV to PYR Bidirectional
        'network': 'BLA',
        'edge': {
            'source': {'pop_name': ['PV']},
            'target': {'pop_name': ['PyrA', 'PyrC']}
        },
        'param': 'PV2PYR_bi',
        'add_properties': 'syn_dist_delay_feng_section_default'
    },
    {  # PYR to PV Bidirectional
        'network': 'BLA',
        'edge': {
            'source': {'pop_name': ['PyrA', 'PyrC']},
            'target': {'pop_name': ['PV']}
        },
        'param': 'PYR2PV_bi',
        'add_properties': 'syn_dist_delay_feng_section_default'
    },
    {  # PYR to SOM Unidirectional
        'network': 'BLA',
        'edge': {
            'source': {'pop_name': ['PyrA', 'PyrC']},
            'target': {'pop_name': ['SOM']}
        },
        'param': 'PYR2SOM',
        'add_properties': 'syn_dist_delay_feng_section_default'
    },
    {  # PYR to VIP Unidirectional
        'network': 'BLA',
        'edge': {
            'source': {'pop_name': ['PyrA', 'PyrC']},
            'target': {'pop_name': ['VIP']}
        },
        'param': 'PYR2VIP',
        'add_properties': 'syn_dist_delay_feng_section_default'
    },
    {  # SOM to PYR Unidirectional
        'network': 'BLA',
        'edge': {
            'source': {'pop_name': ['SOM']},
            'target': {'pop_name': ['PyrA', 'PyrC']}
        },
        'param': 'SOM2PYR',
        'add_properties': 'SOM_rule'
    },
    {  # VIP to SOM Unidirectional
        'network': 'BLA',
        'edge': {
            'source': {'pop_name': ['VIP']},
            'target': {'pop_name': ['SOM']}
        },
        'param': 'VIP2SOM',
        'add_properties': 'syn_dist_delay_feng_section_default'
    },
    {  # SOM to VIP Unidirectional
        'network': 'BLA',
        'edge': {
            'source': {'pop_name': ['SOM']},
            'target': {'pop_name': ['VIP']}
        },
        'param': 'SOM2VIP',
        'add_properties': 'SOM_rule'
    },
    {  # PV to SOM Unidirectional
        'network': 'BLA',
        'edge': {
            'source': {'pop_name': ['PV']},
            'target': {'pop_name': ['SOM']}
        },
        'param': 'PV2SOM',
        'add_properties': 'syn_dist_delay_feng_section_default'
    },
    {  # SOM to PV Unidirectional
        'network': 'BLA',
        'edge': {
            'source': {'pop_name': ['SOM']},
            'target': {'pop_name': ['PV']}
        },
        'param': 'SOM2PV',
        'add_properties': 'SOM_rule'
    },
    #{  # SOM to PV Bidirectional
    #    'network': 'BLA',
    #    'edge': {
    #        'source': {'pop_name': ['SOM']},
    #        'target': {'pop_name': ['PV']}
    #    },
    #    'param': 'SOM2PV_bi',
    #    'add_properties': 'SOM_rule'
    #},
    # {   # PYR to CR Unidirectional
    #    'network':'BLA',
    #    'edge': {
    #        'source':{'pop_name': ['PyrA','PyrC']},
    #        'target':{'pop_name': ['CR']}
    #    },
    #    'param': 'PYR2CR',
    #    'add_properties': 'syn_dist_delay_feng_section_default'
    # },
    # {   # CR to PYR Unidirectional
    #    'network':'BLA',
    #    'edge': {
    #        'source':{'pop_name': ['CR']},
    #        'target':{'pop_name': ['PyrA','PyrC']}
    #    },
    #    'param': 'CR2PYR',
    #    'add_properties': 'syn_dist_delay_feng_section_default'
    # },
    # {   # CR to PV Unidirectional
    #    'network':'BLA',
    #    'edge': {
    #        'source':{'pop_name': ['CR']},
    #        'target':{'pop_name': ['PV']}
    #    },
    #    'param': 'CR2PV',
    #    'add_properties': 'syn_dist_delay_feng_section_default'
    # },
    # {   # CR to SOM Unidirectional
    #    'network':'BLA',
    #    'edge': {
    #        'source':{'pop_name': ['CR']},
    #        'target':{'pop_name': ['SOM']}
    #    },
    #    'param': 'CR2SOM',
    #    'add_properties': 'syn_dist_delay_feng_section_default'
    # },
    ##################### THALAMIC INPUT #####################

    {  # Thalamus to Pyramidal
        'network': 'BLA',
        'edge': {
            'source': networks['thalamus_pyr_A'].nodes(),
            'target': networks['BLA'].nodes(pop_name=['PyrA'])
        },
        'param': 'THALAMUS2PYRA',
        'add_properties': 'syn_uniform_delay_section_default'
    },
    {  # Thalamus to Pyramidal
        'network': 'BLA',
        'edge': {
            'source': networks['thalamus_pyr_C'].nodes(),
            'target': networks['BLA'].nodes(pop_name=['PyrC'])
        },
        'param': 'THALAMUS2PYRC',
        'add_properties': 'syn_uniform_delay_section_default'
    },
    {  # Thalamus to PV
        'network': 'BLA',
        'edge': {
            'source': networks['thalamus_pv'].nodes(),
            'target': networks['BLA'].nodes(pop_name=['PV'])
        },
        'param': 'THALAMUS2PV',
        'add_properties': 'syn_uniform_delay_section_default'
    },
    {  # Thalamus to SOM
        'network': 'BLA',
        'edge': {
            'source': networks['thalamus_som'].nodes(),
            'target': networks['BLA'].nodes(pop_name='SOM')
        },
        'param': 'THALAMUS2SOM',
        'add_properties': 'syn_uniform_delay_section_default'
    },
    {  # Thalamus to VIP
        'network': 'BLA',
        'edge': {
            'source': networks['thalamus_vip'].nodes(),
            'target': networks['BLA'].nodes(pop_name='VIP')
        },
        'param': 'THALAMUS2VIP',
        'add_properties': 'syn_uniform_delay_section_default'
    },
    # {   # Thalamus  to CR
    #    'network':'BLA',
    #    'edge': {
    #        'source':networks['thalamus_cr'].nodes(),
    #        'target':networks['BLA'].nodes(pop_name='CR')
    #    },
    #    'param': 'THALAMUS2CR',
    #    'add_properties': 'syn_uniform_delay_section_default'
    # },
    {  # Tone to PN
        'network': 'BLA',
        'edge': {
            'source': networks['tone'].nodes(),
            'target': networks['BLA'].nodes(pop_name=['PyrA', 'PyrC'])
        },
        'param': 'TONE2PN',
        'add_properties': 'syn_uniform_delay_section_default'
    },
    {  # Tone to PV
        'network': 'BLA',
        'edge': {
            'source': networks['tone'].nodes(),
            'target': networks['BLA'].nodes(pop_name=['PV'])
        },
        'param': 'TONE2PV',
        'add_properties': 'syn_uniform_delay_section_default'
    },
    {  # Tone to VIP
        'network': 'BLA',
        'edge': {
            'source': networks['tone'].nodes(),
            'target': networks['BLA'].nodes(pop_name=['VIP'])
        },
        'param': 'TONE2VIP',
        'add_properties': 'syn_uniform_delay_section_default'
    },
    {  # shock to PV and SOM
        'network': 'BLA',
        'edge': {
            'source': networks['shock'].nodes(),
            'target': networks['BLA'].nodes(pop_name=['PV', 'SOM'])
        },
        'param': 'SHOCK2INT',
        'add_properties': 'syn_uniform_delay_section_default'
    }
]

# edge_params should contain additional parameters to be added to add_edges calls
edge_params = {
    'PYR2PYR': {
        'iterator': 'one_to_one',
        'connection_rule': rand_percent_connector,
        'connection_params': {'prob': 0.09},  # good
        'syn_weight': 1,
        'dynamics_params': 'PN2PN.json',
        'distance_range': [0, max_conn_dist],
        'target_sections': ['apical']
    },
    'PV2PV': {
        'iterator': 'one_to_all',
        'connection_rule': syn_percent_o2a,
        'connection_params': {'p': 0.27, 'no_recip': True, 'track_list': int2int_temp_list, 'max_dist': max_conn_dist}, #0.22
        'syn_weight': 1,
        'dynamics_params': 'PV2PV.json',
        'distance_range': [min_conn_dist, max_conn_dist],
        'target_sections': ['somatic']
    },
    'PV2PV_bi_1': {
        'iterator': 'one_to_all',
        'connection_rule': syn_percent_o2a,
        'connection_params': {'p': 0.0275, 'track_list': uncoupled_bi_track, 'max_dist': max_conn_dist},
        'syn_weight': 1,
        'dynamics_params': 'PV2PV.json',
        'distance_range': [min_conn_dist, max_conn_dist],
        'target_sections': ['somatic']
    },
    'PV2PV_bi_2': {
        'iterator': 'one_to_all',
        'connection_rule': recurrent_connector_o2a,
        'connection_params': {'p': 1, 'all_edges': uncoupled_bi_track},
        'syn_weight': 1,
        'dynamics_params': 'PV2PV.json',
        'distance_range': [min_conn_dist, max_conn_dist],
        'target_sections': ['somatic']
    },
    'PV2PYR': {
        'iterator': 'one_to_all',
        'connection_rule': syn_percent_o2a,
        'connection_params': {'p': 0.48, 'max_dist': max_conn_dist},  # {'p':0.41},
        'syn_weight': 1,
        'dynamics_params': 'PV2PN.json',
        'distance_range': [min_conn_dist, max_conn_dist],
        'target_sections': ['somatic']
    },
    'PYR2PV': {
        'iterator': 'one_to_all',
        'connection_rule': syn_percent_o2a,
        'connection_params': {'p': 0.32, 'angle_dist': False, 'max_dist': max_conn_dist, 'angle_dist_radius': 100}, #0.22
        'syn_weight': 1,
        'dynamics_params': 'PN2PV.json',
        'distance_range': [min_conn_dist, max_conn_dist],
        'target_sections': ['basal']
    },
    'PV2PYR_bi': {
        'iterator': 'one_to_all',
        'connection_rule': syn_percent_o2a,
        'connection_params': {'p': 0.09, 'track_list': pyr_int_bi_list, 'max_dist': max_conn_dist}, #0.09
        'syn_weight': 1,
        'dynamics_params': 'PV2PN.json',
        'distance_range': [min_conn_dist, max_conn_dist],
        'target_sections': ['somatic']
    },
    'PYR2PV_bi': {
        'iterator': 'one_to_all',
        'connection_rule': recurrent_connector_o2a,
        'connection_params': {'p': 1, 'all_edges': pyr_int_bi_list},  # was 1
        'syn_weight': 1,
        'dynamics_params': 'PN2PV.json',
        'distance_range': [min_conn_dist, max_conn_dist],
        'target_sections': ['basal']
    },
    'PYR2SOM': {
        'iterator': 'one_to_all',
        'connection_rule': syn_percent_o2a,
        'connection_params': {'p': 0.35, 'angle_dist': False, 'max_dist': max_conn_dist, 'angle_dist_radius': 100},#0.31
        'syn_weight': 1,
        'dynamics_params': 'PN2SOM.json',
        'distance_range': [min_conn_dist, max_conn_dist],
        'target_sections': ['basal']
    },
    'PYR2VIP': {
        'iterator': 'one_to_all',
        'connection_rule': syn_percent_o2a,
        'connection_params': {'p': 0.35, 'angle_dist': False, 'max_dist': max_conn_dist, 'angle_dist_radius': 100},#0.31
        'syn_weight': 1,
        'dynamics_params': 'PN2VIP.json',
        'distance_range': [min_conn_dist, max_conn_dist],
        'target_sections': ['basal']
    },
    'SOM2PYR': {
        'iterator': 'one_to_all',
        'connection_rule': syn_percent_o2a,
        'connection_params': {'p': 0.35, 'max_dist': max_conn_dist}, #0.066
        'syn_weight': 1,
        'dynamics_params': 'SOM2PN.json',
        'distance_range': [min_conn_dist, max_conn_dist],
        'target_sections': ['apical']
    },
    'PV2SOM': {
        'iterator':'one_to_all', #0.55
        'connection_rule':syn_percent_o2a,
        'connection_params':{'p':0.4, 'track_list': PV2SOM_bi_list, 'max_dist':max_conn_dist},
        'syn_weight':1,
        'dynamics_params':'PV2SOM.json',
        'distance_range':[min_conn_dist,max_conn_dist],
        'target_sections':['somatic']
    },
    'SOM2PV': {
        'iterator': 'one_to_all',
        'connection_rule': syn_percent_o2a,
        'connection_params': {'p': 0.65, 'max_dist':max_conn_dist},
        'syn_weight': 1,
        'dynamics_params': 'SOM2PV.json',
        'distance_range': [min_conn_dist, max_conn_dist],
        'target_sections': ['apical']
    },
    'SOM2PV_bi': {
        'iterator': 'one_to_all',
        'connection_rule': recurrent_connector_o2a,
        'connection_params': {'p': 0.0001, 'all_edges': PV2SOM_bi_list},
        'syn_weight': 1,
        'dynamics_params': 'SOM2PV.json',
        'distance_range': [min_conn_dist, max_conn_dist],
        'target_sections': ['apical']
    },
    'VIP2SOM': {
        'iterator': 'one_to_all', # 0.55
        'connection_rule': syn_percent_o2a,
        'connection_params': {'p': 0.55, 'track_list': VIP2SOM_bi_list, 'max_dist': max_conn_dist},
        'syn_weight': 1,
        'dynamics_params': 'VIP2SOM.json',
        'distance_range': [min_conn_dist, max_conn_dist],
        'target_sections': ['apical']
    },
    'SOM2VIP': {
        'iterator': 'one_to_all',
        'connection_rule': recurrent_connector_o2a,  # 0.55
        'connection_params': {'p': 1, 'all_edges': VIP2SOM_bi_list},
        'syn_weight': 1,
        'dynamics_params': 'SOM2VIP.json',
        'distance_range': [min_conn_dist, max_conn_dist],
        'target_sections': ['apical']
    },
    # 'PYR2CR': {
    #    'iterator':'one_to_one',
    #    'connection_rule':rand_percent_connector,
    #    'connection_params':{'prob':0.08}, # needs more
    #    'syn_weight':1,
    #    'dynamics_params':'PN2CR_tyler.json',
    #    'distance_range':[min_conn_dist,max_conn_dist],
    #    'target_sections':['basal']
    # },
    # 'CR2PYR': {
    #    'iterator':'one_to_one',
    #    'connection_rule':rand_percent_connector,
    #    'connection_params':{'prob':0.1}, #needs more
    #    'syn_weight':1,
    #    'dynamics_params':'CR2PN_tyler.json',
    #    'distance_range':[min_conn_dist,max_conn_dist],
    #    'target_sections':['somatic']
    # },
    # 'CR2PV': {
    #    'iterator':'one_to_one',
    #    'connection_rule':rand_percent_connector,
    #    'connection_params':{'prob':0.067}, # good
    #    'syn_weight':1,
    #    'dynamics_params':'CR2INT_tyler.json',
    #    'distance_range':[min_conn_dist,max_conn_dist],
    #    'target_sections':['basal']
    # },
    # 'CR2SOM': {
    #    'iterator':'one_to_one',
    #    'connection_rule':rand_percent_connector,
    #    'connection_params':{'prob':0.075}, # nees less
    #    'syn_weight':1,
    #    'dynamics_params':'CR2SOM_tyler.json',
    #    'distance_range':[min_conn_dist,max_conn_dist],
    #    'target_sections':['basal']
    # },
    'THALAMUS2PYRA': {
        'connection_rule': one_to_one,
        'syn_weight': 1,
        'dynamics_params': 'BG2PN_A.json',
        'distance_range': [0.0, 9999.9],
        'target_sections': ['apical']
    },
    'THALAMUS2PYRC': {
        'connection_rule': one_to_one_offset,
        'connection_params': {'offset': numPN_A},
        'syn_weight': 1,
        'dynamics_params': 'BG2PN_C.json',
        'distance_range': [0.0, 9999.9],
        'target_sections': ['apical']
    },
    'THALAMUS2PV': {
        'connection_rule': one_to_one_offset,
        'connection_params': {'offset': numPN_A + numPN_C},
        'syn_weight': 1,
        'dynamics_params': 'BG2PV.json',
        'distance_range': [0.0, 9999.9],
        'target_sections': ['basal']
    },
    'THALAMUS2SOM': {
        'connection_rule': one_to_one_offset,
        'connection_params': {'offset': numPN_A + numPN_C + numPV},
        'syn_weight': 1,
        'target_sections': ['basal'],
        'distance_range': [0.0, 9999.9],
        'dynamics_params': 'BG2SOM.json'
    },
	'THALAMUS2VIP': {
        'connection_rule': one_to_one_offset,
        'connection_params': {'offset': numPN_A + numPN_C + numPV + numSOM},
        'syn_weight': 1,
        'target_sections': ['basal'],
        'distance_range': [0.0, 9999.9],
        'dynamics_params': 'BG2VIP.json'
    },
    # 'THALAMUS2CR': {
    #    'connection_rule':one_to_one_offset,
    #    'connection_params':{'offset':numPN_A+numPN_C+numPV+numSOM},
    #    'syn_weight':1,
    #    'target_sections':['basal'],
    #    'distance_range':[0.0, 9999.9],
    #    'dynamics_params':'BG2CR_thalamus_min.json'
    # },
    'TONE2PN': {
        'connection_rule': rand_percent_connector,
        'connection_params': {'prob': 0.7},
        'syn_weight': 1,
        'target_sections': ['apical'],
        'distance_range': [0.0, 9999.9],
        'dynamics_params': 'tone2PN.json'
    },
    'TONE2PV': {
        'connection_rule': rand_percent_connector,
        'connection_params': {'prob': 0.7},
        'syn_weight': 1,
        'target_sections': ['basal'],
        'distance_range': [0.0, 9999.9],
        'dynamics_params': 'tone2PV.json'
    },
    'TONE2VIP': {
        'connection_rule': rand_percent_connector,
        'connection_params': {'prob': 0.7},
        'syn_weight': 1,
        'target_sections': ['basal'],
        'distance_range': [0.0, 9999.9],
        'dynamics_params': 'tone2VIP.json'
    },
    'SHOCK2INT': {
        'connection_rule': rand_shock_connector,
        'connection_params': {'prob': 0.7},
        'syn_weight': 1,
        'target_sections': ['basal'],
        'distance_range': [0.0, 9999.9],
        'dynamics_params': 'shock2INT12.json'
    }
}  # edges referenced by name

# Will be called by conn.add_properties for the associated connection
edge_add_properties = {
    'syn_dist_delay_feng_section_default': {
        'names': ['delay', 'sec_id', 'sec_x'],
        'rule': syn_dist_delay_feng_section,
        'rule_params': {'sec_x': 0.9},
        'dtypes': [np.float, np.int32, np.float]
    },
    'syn_uniform_delay_section_default': {
        'names': ['delay', 'sec_id', 'sec_x'],
        'rule': syn_uniform_delay_section,
        'rule_params': {'sec_x': 0.9},
        'dtypes': [np.float, np.int32, np.float]
    },
    'SOM_rule': {
        'names': ['delay', 'sec_id', 'sec_x'],
        'rule': syn_uniform_delay_section,
        'rule_params': {'sec_x': 0.6},
        'dtypes': [np.float, np.int32, np.float]
    }
}

##########################################################################
############################  EDGE EFFECTS  ##############################

if edge_effects:
    # These rules are for edge effect edges. They should directly mimic the connections
    # created previously, re-use the params set above. This keeps our code DRY
    virt_edges = [
        {  # Pyramidal to Pyramidal Connections
            'network': 'BLA',
            'edge': {
                'source': networks['shell'].nodes(**{'pop_name': ['PyrA', 'PyrC']}),
                'target': {'pop_name': ['PyrA', 'PyrC']}
            },
            'param': 'PYR2PYR',
            'add_properties': 'syn_dist_delay_feng_section_default'
        },
        {  # PV to PV Uncoupled Unidirectional
            'network': 'BLA',
            'edge': {
                'source': networks['shell'].nodes(**{'pop_name': ['PV']}),
                'target': {'pop_name': ['PV']}
            },
            'param': 'PV2PV',
            'add_properties': 'syn_dist_delay_feng_section_default'
        },
        # PV to PV Uncoupled Bidirectional Pair N/A
        # PV to PV Uncoupled Bidirectional Pair N/A
        {  # PV to PYR Unidirectional
            'network': 'BLA',
            'edge': {
                'source': networks['shell'].nodes(**{'pop_name': ['PV']}),
                'target': {'pop_name': ['PyrA', 'PyrC']}
            },
            'param': 'PV2PYR',
            'add_properties': 'syn_dist_delay_feng_section_default'
        },
        {  # PYR to PV Unidirectional
            'network': 'BLA',
            'edge': {
                'source': networks['shell'].nodes(**{'pop_name': ['PyrA', 'PyrC']}),
                'target': {'pop_name': ['PV']}
            },
            'param': 'PYR2PV',
            'add_properties': 'syn_dist_delay_feng_section_default'
        },
        # PV to PYR Bidirectional N/A
        # PYR to PV Bidirectional N/A
        {  # PYR to SOM Unidirectional
            'network': 'BLA',
            'edge': {
                'source': networks['shell'].nodes(**{'pop_name': ['PyrA', 'PyrC']}),
                'target': {'pop_name': ['SOM']}
            },
            'param': 'PYR2SOM',
            'add_properties': 'syn_dist_delay_feng_section_default'
        },
        {  # SOM to PYR Unidirectional
            'network': 'BLA',
            'edge': {
                'source': networks['shell'].nodes(**{'pop_name': ['SOM']}),
                'target': {'pop_name': ['PyrA', 'PyrC']}
            },
            'param': 'SOM2PYR',
            'add_properties': 'syn_dist_delay_feng_section_default'
        },
        {  # PV to SOM Unidirectional
            'network': 'BLA',
            'edge': {
                'source': networks['shell'].nodes(**{'pop_name': ['PV']}),
                'target': {'pop_name': ['SOM']}
            },
            'param': 'PV2SOM',
            'add_properties': 'syn_dist_delay_feng_section_default'
        },
        {  # PYR to CR Unidirectional
            'network': 'BLA',
            'edge': {
                'source': networks['shell'].nodes(**{'pop_name': ['PyrA', 'PyrC']}),
                'target': {'pop_name': ['CR']}
            },
            'param': 'PYR2CR',
            'add_properties': 'syn_dist_delay_feng_section_default'
        },
        {  # CR to PYR Unidirectional
            'network': 'BLA',
            'edge': {
                'source': networks['shell'].nodes(**{'pop_name': ['CR']}),
                'target': {'pop_name': ['PyrA', 'PyrC']}
            },
            'param': 'CR2PYR',
            'add_properties': 'syn_dist_delay_feng_section_default'
        },
        {  # CR to PV Unidirectional
            'network': 'BLA',
            'edge': {
                'source': networks['shell'].nodes(**{'pop_name': ['CR']}),
                'target': {'pop_name': ['PV']}
            },
            'param': 'CR2PV',
            'add_properties': 'syn_dist_delay_feng_section_default'
        },
        {  # CR to SOM Unidirectional
            'network': 'BLA',
            'edge': {
                'source': networks['shell'].nodes(**{'pop_name': ['CR']}),
                'target': {'pop_name': ['SOM']}
            },
            'param': 'CR2SOM',
            'add_properties': 'syn_dist_delay_feng_section_default'
        }
    ]

    edge_definitions = edge_definitions + virt_edges
##########################################################################
########################## END EDGE EFFECTS ##############################


##########################################################################
###############################  BUILD  ##################################

# Load synapse dictionaries
# see synapses.py - loads each json's in components/synaptic_models into a
# dictionary so the properties can be referenced in the files eg: syn['file.json'].get('property')
synapses.load()
syn = synapses.syn_params_dicts()

# Build your edges into the networks
build_edges(networks, edge_definitions, edge_params, edge_add_properties, syn)

# Save the network into the appropriate network dir
save_networks(networks, network_dir)

if edge_effects:
    from scipts_that_might_help_later.build_input_shell import build_shell_inputs

    # This needs to be called after building and saving your networks
    # There's an optimization in there that determines which shells in the
    # shell are connected to bio cells, and only delivers a spike train to
    # those, excluding others and speeding up the simulation.
    # Since edges are semi-random, we want to deliver to the correct cells
    # each time.
    build_shell_inputs()

from build_input import build_input

build_input(t_sim,
            numPN_A=569,
            numPN_C=231,
            numPV=93,
            numSOM=107,
            numCR=0,
            scale=4)

# Usually not necessary if you've already built your simulation config
"""
build_env_bionet(base_dir='./',
	network_dir=network_dir,
	tstop=t_sim, dt = dt,
	report_vars = ['v'],
    v_init = -70.0,
    celsius = 31.0,
	spikes_inputs=[
        ('thalamus_pyr_A','inputs/thalamus_pyr_A_spikes.h5'),
        ('thalamus_pyr_C','inputs/thalamus_pyr_C_spikes.h5'),
        ('thalamus_pv','inputs/thalamus_pv_spikes.h5'),
        ('thalamus_som','inputs/thalamus_som_spikes.h5'),
        ('thalamus_vip','inputs/thalamus_vip_spikes.h5')],
	components_dir=components_dir,
    config_file='simulation_config.json',
	compile_mechanisms=False)
"""
