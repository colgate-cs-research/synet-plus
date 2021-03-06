#!/usr/bin/env python

"""
Test various grid sizes
"""

import random
import unittest
from nose.plugins.attrib import attr

from synet.synthesis.connected import ConnectedSyn
import synet.synthesis.ospf_heuristic
import synet.synthesis.ospf

from synet.utils.common import Protocols
from synet.utils.common import PathReq
from synet.utils.common import random_requirement_path
from synet.utils.topo_gen import gen_grid_topology


__author__ = "Ahmed El-Hassany"
__email__ = "a.hassany@gmail.com"


@attr(speed='slow')
class TestOSPFGrid(unittest.TestCase):
    def setUp(self):
        self.random = random.Random(3010720575261890242)

    def generate_paths(self, g, reqsize):
        """
        Generate a random set of path requirements that are guaranteed
        to be satisfiable
        :param g: Network topology
        :param reqsize: the number of required path
        :return: list of PathReq
        """
        routers = [n for n in g.local_routers_iter()]
        paths = []
        # Generate the required paths
        for i in range(0, reqsize):
            src, dst = self.random.sample(routers, 2)
            assert src != dst
            path = random_requirement_path(g, src, dst, random_obj=self.random,
                                           tmp_weight_name='test-weight')
            paths.append(path)
        reqs = []
        for path in paths:
            reqs.append(PathReq(Protocols.OSPF, path[-1], path, False))
        return reqs

    def gen_grid(self, n, m, nets):
        grid = gen_grid_topology(n, m, nets)
        for node in grid.local_routers_iter():
            grid.enable_ospf(node, 100)
        conn_syn = ConnectedSyn([], grid, full=True)
        conn_syn.synthesize()
        return grid

    @attr(speed='fast')
    def test_grid2_1path_no_heurisitc(self):
        g = self.gen_grid(2, 2, 1)
        paths = self.generate_paths(g, 1)
        ospf = synet.synthesis.ospf.OSPFSyn(g)
        for req in paths:
            ospf.add_req(req)
        self.assertTrue(ospf.solve())

    @attr(speed='fast')
    def test_grid2_1path_heurisitc(self):
        g = self.gen_grid(2, 2, 1)
        reqs = self.generate_paths(g, 1)
        ospf = synet.synthesis.ospf_heuristic.OSPFSyn(g, random_obj=self.random)
        for req in reqs:
            ospf.add_req(req)
        self.assertTrue(ospf.synthesize())
        self.assertEqual(len(ospf.reqs), 1)
        self.assertEqual(len(ospf.removed_reqs), 0)

    @attr(speed='fast')
    def test_grid2_2path_no_heurisitc(self):
        g = self.gen_grid(2, 2, 1)
        paths = self.generate_paths(g, 2)
        ospf = synet.synthesis.ospf.OSPFSyn(g)
        for req in paths:
            ospf.add_req(req)
        self.assertTrue(ospf.solve())

    @attr(speed='fast')
    def test_grid2_2path_heurisitc(self):
        g = self.gen_grid(2, 2, 1)
        reqs = self.generate_paths(g, 2)
        ospf = synet.synthesis.ospf_heuristic.OSPFSyn(g, random_obj=self.random)
        for req in reqs:
            ospf.add_req(req)
        self.assertTrue(ospf.synthesize())
        self.assertEqual(len(ospf.reqs), 2)
        self.assertEqual(len(ospf.removed_reqs), 0)

    def test_grid3_1path_no_heurisitc(self):
        g = self.gen_grid(3, 3, 1)
        reqs = self.generate_paths(g, 1)
        ospf = synet.synthesis.ospf.OSPFSyn(g)
        for req in reqs:
            ospf.add_req(req)
        self.assertTrue(ospf.solve())

    def test_grid3_1path_heurisitc(self):
        g = self.gen_grid(3, 3, 1)
        reqs = self.generate_paths(g, 1)
        ospf = synet.synthesis.ospf_heuristic.OSPFSyn(g, random_obj=self.random)
        for req in reqs:
            ospf.add_req(req)
        self.assertTrue(ospf.synthesize())
        self.assertEqual(len(ospf.reqs), 1)
        self.assertEqual(len(ospf.removed_reqs), 0)

    def test_grid3_2path_no_heurisitc(self):
        g = self.gen_grid(3, 3, 1)
        reqs = self.generate_paths(g, 2)
        ospf = synet.synthesis.ospf.OSPFSyn(g)
        for req in reqs:
            ospf.add_req(req)
        self.assertTrue(ospf.solve())

    def test_grid3_2path_heurisitc(self):
        g = self.gen_grid(3, 3, 1)
        reqs = self.generate_paths(g, 2)
        ospf = synet.synthesis.ospf_heuristic.OSPFSyn(g, random_obj=self.random)
        for req in reqs:
            ospf.add_req(req)
        self.assertTrue(ospf.synthesize())
        self.assertEqual(len(ospf.reqs), 2)
        self.assertEqual(len(ospf.removed_reqs), 0)

    def test_grid4_1path_no_heurisitc(self):
        g = self.gen_grid(4, 4, 1)
        reqs = self.generate_paths(g, 1)
        ospf = synet.synthesis.ospf.OSPFSyn(g)
        for req in reqs:
            ospf.add_req(req)
        self.assertTrue(ospf.solve())

    def test_grid4_1path_heurisitc(self):
        g = self.gen_grid(4, 4, 1)
        reqs = self.generate_paths(g, 1)
        ospf = synet.synthesis.ospf_heuristic.OSPFSyn(g, random_obj=self.random)
        for req in reqs:
            ospf.add_req(req)
        self.assertTrue(ospf.synthesize())
        self.assertEqual(len(ospf.reqs), 1)
        self.assertEqual(len(ospf.removed_reqs), 0)

    def test_grid4_2path_no_heurisitc(self):
        g = self.gen_grid(4, 4, 1)
        reqs = self.generate_paths(g, 2)
        ospf = synet.synthesis.ospf.OSPFSyn(g)
        for req in reqs:
            ospf.add_req(req)
        self.assertTrue(ospf.solve())


    def test_grid4_2path_heurisitc(self):
        g = self.gen_grid(4, 4, 1)
        reqs = self.generate_paths(g, 2)
        ospf = synet.synthesis.ospf_heuristic.OSPFSyn(g, random_obj=self.random)
        for req in reqs:
            ospf.add_req(req)
        self.assertTrue(ospf.synthesize())
        self.assertEqual(len(ospf.reqs), 2)
        self.assertEqual(len(ospf.removed_reqs), 0)

    def test_grid5_1path_no_heurisitc(self):
        g = self.gen_grid(5, 5, 1)
        reqs = self.generate_paths(g, 1)
        ospf = synet.synthesis.ospf.OSPFSyn(g)
        for req in reqs:
            ospf.add_req(req)
        self.assertTrue(ospf.solve())

    def test_grid5_1path_heurisitc(self):
        g = self.gen_grid(5, 5, 1)
        reqs = self.generate_paths(g, 1)
        ospf = synet.synthesis.ospf_heuristic.OSPFSyn(g, random_obj=self.random)
        for req in reqs:
            ospf.add_req(req)
        self.assertTrue(ospf.synthesize())
        self.assertEqual(len(ospf.reqs), 1)
        self.assertEqual(len(ospf.removed_reqs), 0)

    def test_grid5_2path_no_heurisitc(self):
        g = self.gen_grid(5, 5, 1)
        reqs = self.generate_paths(g, 2)
        ospf = synet.synthesis.ospf.OSPFSyn(g)
        for req in reqs:
            ospf.add_req(req)
        self.assertTrue(ospf.solve())

    def test_grid5_2path_heurisitc(self):
        g = self.gen_grid(5, 5, 1)
        reqs = self.generate_paths(g, 2)
        ospf = synet.synthesis.ospf_heuristic.OSPFSyn(g, random_obj=self.random)
        for req in reqs:
            ospf.add_req(req)
        self.assertTrue(ospf.synthesize())
        self.assertEqual(len(ospf.reqs), 2)
        self.assertEqual(len(ospf.removed_reqs), 0)
