"""Compare the 1-loop SMEFT matching based on aXiv:1908.05295
numerically to the Mathematica code provided by the authors."""

import unittest
import numpy as np
import numpy.testing as npt
from math import sqrt, pi
import wcxf
import wilson
import wilson.match.smeft_loop
from copy import deepcopy


C_zero = wilson.util.smeftutil.C_array2dict(np.zeros(9999))


_g1b = 0.35
_mW = 80.4
_vT = 246
_g2b = 2 * _mW / _vT
# Here it is assumed that phiWB and phiD vanish!
p = {
    "GF": 1 / sqrt(2) / _vT**2,
    "m_W": _mW, "m_h": 125, "m_t": 173,
    "alpha_s": 1.2**2 / (4 * pi),
    "alpha_e": (_g1b**2 * _g2b**2) / (4 * pi *(_g1b**2 + _g2b**2)),
    "mZ": _vT / 2 * sqrt(_g1b**2 + _g2b**2),
    "m_d": 0.005, "m_s": 0.1, "m_b": 4.2, "m_u": 0.004, "m_c": 1.2,
    "m_e": 0.0005, "m_mu": 0.1, "m_tau": 1.8}


test_dicts = {
    'G': {"G": 0.00667139, ("uG", (2, 2)): -0.0030563},
    ('VeuLL', (0, 1, 1, 0)): {("lq1", (0, 1, 1, 0)): 0.00484751, ("lq3", (0, 1, 1, 0)): -0.0476133},
    ('VeuLL', (0, 0, 1, 1)): {'phi': 0.0135966, 'phiB': 0.0215244, 'phiBox': 0.0188167, 'phiW': -0.0264041, 'W': 0.00972366,
                              ("phil1", (0, 0)): 0.0109503,
                            #   ("phil3", (0, 0)): 0.0397606,
                              ("phiq1", (1, 1)): -0.0114492, ("phiq1", (2, 2)): -0.0113446, ("phiq3", (1, 1)): 0.0401106,
                              ("phiq3", (2, 2)): 0.0113446, ("phiu", (2, 2)): 0.0100831, ("lq1", (0, 0, 1, 1)): 0.00484751,
                              ("lq1", (0, 0, 2, 2)): 0.0100553, ("lq3", (0, 0, 1, 1)): -0.0476133, ("lq3", (0, 0, 2, 2)): -0.0100553,
                              ("lu", (0, 0, 2, 2)): -0.00927121,
                              ("qq1", (1, 1, 2, 2)): -0.0082092, ("qq1", (1, 2, 2, 1)): -0.0064767, 
                              ("qq3", (1, 1, 2, 2)): -0.0082092, ("qq3", (1, 2, 2, 1)): -0.0064767, 
                              ("qu1", (1, 1, 2, 2)): 0.00703301,
                              ("uB", (2, 2)): 0.000932991, ("uphi", (2, 2)): -0.0151402, ("uW", (2, 2)): -0.0110162},

    ('VnunuLL', (1, 1, 2, 2)): {'phi': -0.00872334, 'phiB': 0.000273223, 'phiBox': -0.0120725, 'phiW': 0.00285751,
                                ("phil1", (1, 1)): 0.00213136, ("phil1", (2, 2)): 0.00213136,
                                # ("phil3", (1, 1)): -0.0054478, ("phil3", (2, 2)): -0.0054478,
                                ("phiq1", (2, 2)): 0.0068738, ("phiq3", (2, 2)): -0.0068738,
                                ("phiu", (2, 2)): -0.0068738,
                                ("ll", (1, 1, 2, 2)): -0.00311008, ("ll", (1, 2, 2, 1)): -0.00311008,
                                ("lq1", (1, 1, 2, 2)): 0.0034369, ("lq1", (2, 2, 2, 2)): 0.0034369,
                                ("lq3", (1, 1, 2, 2)): 0.0034369, ("lq3", (2, 2, 2, 2)): 0.0034369,
                                ("lu", (1, 1, 2, 2)): -0.0034369, ("lu", (2, 2, 2, 2)): -0.0034369,
                                ("uphi", (2, 2)): 0.00971366},
    ('V8udduLR', (0, 0, 1, 1)): {("phiud", (1, 1)): 0.0347041},
    ('SnueduRR', (0, 1, 2, 1)): {("lequ1", (0, 1, 2, 1)): 0.00300076, ("lequ3", (0, 1, 2, 1)): 0.0148086},
    ('V1ddLR', (0, 2, 2, 0)): {("qd1", (0, 2, 2, 0)): -0.00220348},
    ('V1ddLR', (2, 2, 0, 0)): {'phi': 0.00441334, 'phiB': -0.00493365, 'phiBox': 0.00610774, 'phiW': 0.00334974, 'W': -0.00248509,
                            ("phid", (0, 0)): -0.010698, ("phiq1", (2, 2)): -0.00305995,
                            ("phiq3", (2, 2)): 0.000707166, ("phiu", (2, 2)): 0.00326459,
                            ("qd1", (2, 2, 0, 0)): -0.00979227, ("qq1", (2, 2, 2, 2)): 0.00369227,
                            ("qq3", (2, 2, 2, 2)): 0.00213381, ("qu1", (2, 2, 2, 2)): -0.0022382,
                            ("uB", (2, 2)): 0.000775004, ("ud1", (2, 2, 0, 0)): 0.00914776,
                            ("uphi", (2, 2)): -0.00491437, ("uW", (2, 2)): 0.000224152},
    ('V8udRR', (1, 1, 2, 2)): {("phid", (2, 2)): -0.0398387, ("phiu", (1, 1)): 0.021593, ("qd8", (2, 2, 2, 2)): 0.0022238,
                            ("qu8", (2, 2, 1, 1)): 0.0022238, ("ud8", (1, 1, 2, 2)): 0.000549022,
                            ("ud8", (2, 2, 2, 2)): 0.0022238, ("uG", (2, 2)): 0.0146702, ("uu", (1, 2, 2, 1)): 0.0105269,
                            },
}

class TestLoopMatch(unittest.TestCase):
    def test_loop_match(self):
        for kwet_jj, mdict in test_dicts.items():
            for k_ii, v in mdict.items():
                C_SMEFT = deepcopy(C_zero)
                if not isinstance(k_ii, tuple):
                    C_SMEFT[k_ii] = 1
                else:
                    k, ii = k_ii
                    C_SMEFT[k][ii] = 1
                C_SMEFT = wilson.util.smeftutil.symmetrize_nonred(C_SMEFT)
                C_WET = wilson.match.smeft_loop.match_all_array(C_SMEFT, p, scale=120)
                if not isinstance(kwet_jj, tuple):
                    v_wet = C_WET[kwet_jj]
                else:
                    kwet, jj = kwet_jj
                    v_wet = C_WET[kwet][jj]
                self.assertAlmostEqual(v_wet, v,
                                       delta=1e-6,
                                       msg="Failed for {} matching into {}".format(k_ii, kwet_jj))
