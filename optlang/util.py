# Copyright (c) 2013 Novo Nordisk Foundation Center for Biosustainability, DTU.
# See LICENSE for details.

"""Utility functions for optlang.

.. moduleauthor:: Nikolaus Sonnenschein <niko.sonnenschein@gmail.com>

"""

import os
import logging
log = logging.getLogger(__name__)
import tempfile
from collections import OrderedDict
from subprocess import check_output
try:
    from glpk.glpkpi import *
except:
    pass


def solve_with_glpsol(glp_prob):
    '''Solve glpk problem with glpsol commandline solver. Mainly for testing purposes.

    # Examples
    # --------

    # >>> problem = glp_create_prob()
    # ... glp_read_lp(problem, None, "../tests/data/model.lp")
    # ... solution = solve_with_glpsol(problem)
    # ... print 'asdf'
    # 'asdf'
    # >>> print solution
    # 0.839784

    # Returns
    # -------
    # dict
    #     A dictionary containing the objective value (key ='objval')
    #     and variable primals.
    '''
    row_ids = [glp_get_row_name(glp_prob, i) for i in xrange(1, glp_get_num_rows(glp_prob)+1)]
    
    col_ids = [glp_get_col_name(glp_prob, i) for i in xrange(1, glp_get_num_cols(glp_prob)+1)]
    
    tmp_file = tempfile.mktemp(suffix='.lp')
    # glp_write_mps(glp_prob, GLP_MPS_DECK, None, tmp_file)
    glp_write_lp(glp_prob, None, tmp_file)
    # with open(tmp_file, 'w') as tmp_handle:
    #     tmp_handle.write(mps_string)
    cmd = ['glpsol', '--lp', tmp_file, '-w', tmp_file+'.sol', '--log', '/dev/null']
    term = check_output(cmd)
    log.info(term)

    with open(tmp_file+'.sol') as sol_handle:
        # print sol_handle.read()
        solution = dict()
        for i, line in enumerate(sol_handle.readlines()):
            if i <= 1 or line == '\n':
                pass
            elif i <= len(row_ids):
                solution[row_ids[i-2]] = line.strip().split(' ')
            elif i <= len(row_ids)+len(col_ids)+1:
                solution[col_ids[i-2-len(row_ids)]] = line.strip().split(' ')
            else:
                print i
                print line
                raise "Argggh!"
    return solution

def glpk_read_cplex(path):
    """Reads cplex file and returns glpk problem.

    Returns
    -------
    glp_prob
        A glpk problems (same type as returned by glp_create_prob)
    """
    problem = glp_create_prob()
    glp_read_lp(problem, None, "../tests/data/model.lp")
    return problem

def list_available_solvers():
    """Determine available solver interfaces (with python bindings).

    Returns
    -------
    dict
        A dict like {'GLPK': True, 'GUROBI': False, ...}
    """
    solvers = dict(GUROBI=False, GLPK=False, MOSEK=False, CPLEX=False)
    try:
        import gurobipy
        solvers['GUROBI'] = True
        log.info('Gurobi python bindings found at %' % os.path.dirname(gurobipy.__file__))
    except:
        log.info('Gurobi python bindings not available.')
    try:
        import glpk.glpkpi
        solvers['GLPK'] = True
        log.info('Gurobi python bindings found at %' % os.path.dirname(glpk.glpkpi.__file__))
    except:
        log.info('GLPK python bindings not available.')
    try:
        import mosek
        solvers['MOSEK'] = True
        log.info('Mosek python bindings found at %' % os.path.dirname(mosek.__file__))
    except:
        log.info('Mosek python bindings not available.')
    try:
        import cplex
        solvers['CPLEX'] = True
        log.info('CPLEX python bindings found at %' % os.path.dirname(cplex.__file__))
    except:
        log.info('CPLEX python bindings not available.')
    return solvers

class Container(OrderedDict):
    """..."""
    def __init__(self, *args, **kwargs):
        super(DictContainer, self).__init__(*args, **kwargs)
        self.arg = arg

if __name__ == '__main__':
    problem = glp_create_prob()
    glp_read_lp(problem, None, "../tests/data/model.lp")
    print "asdf", glp_get_num_rows(problem)
    solution = solve_with_glpsol(problem)
    print solution['R_Biomass_Ecoli_core_w_GAM']
        