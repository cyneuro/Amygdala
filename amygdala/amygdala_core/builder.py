from bmtk.builder import NetworkBuilder

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

def build_edges(networks, edge_definitions, edge_params, edge_add_properties, syn=None): 
    # Builds the edges for each network given a set of 'edge_definitions'
    # edge_definitions examples shown later in the code
    for edge in edge_definitions: 
        network_name = edge['network']
        edge_src_trg = edge['edge']
        edge_params_val = edge_params[edge['param']]
        dynamics_file = edge_params_val['dynamics_params']
        model_template = syn[dynamics_file]['level_of_detail']

        model_template_kwarg = {'model_template': model_template}

        net = networks[network_name]

        conn = net.add_edges(**edge_src_trg, **edge_params_val, **model_template_kwarg)
        
        if edge.get('add_properties'): 
            edge_add_properties_val = edge_add_properties[edge['add_properties']]
            conn.add_properties(**edge_add_properties_val)

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