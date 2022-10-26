# -*- coding: utf-8 -*-
import os, sys
from bmtk.simulator import bionet
import warnings

def run(config_file):

    warnings.simplefilter(action='ignore', category=FutureWarning)

    conf = bionet.Config.from_json(config_file, validate=True)
    conf.build_env()

    graph = bionet.BioNetwork.from_config(conf)

    # This fixes the morphology error in LFP calculation
    pop = graph._node_populations['BLA']
    for node in pop.get_nodes():
        node._node._node_type_props['morphology'] = node.model_template[1]

    sim = bionet.BioSimulator.from_config(conf, network=graph)

    # This calls insert_mechs() on each cell to use its gid as a seed
    # to the random number generator, so that each cell gets a different
    # random seed for the point-conductance noise
    #cells = graph.get_local_cells()
    #for cell in cells:
    #    cells[cell].hobj.insert_mechs(cells[cell].gid)
    sim.run()
    bionet.nrn.quit_execution()

if __name__ == '__main__':
    if __file__ != sys.argv[-1]:
        run(sys.argv[-1])
    else:
        run('simulation_config.ccl.json')
