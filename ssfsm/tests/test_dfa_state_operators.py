from unittest import TestCase

import ssfsm

class TestStateOperators(TestCase):
    m = None

    def setUp(self):
        B = ssfsm.Machine(0) # B has aa
        B[0]['a'] = B[1]
        B[0]['b'] = B[0]
        B[1]['a'] = B[2]
        B[1]['b'] = B[0]
        B[2] = True
        B[2]['ab'] = B[2]
        B[3]

        self.m = B

    def test_follwoing(self):
        m = self.m
        self.assertTrue(m[0] > m[1])
        self.assertTrue(m[0] > m[0])
        self.assertTrue(m[1] > m[2])
        self.assertTrue(m[1] > m[0])
        self.assertTrue(m[2] > m[2])
        self.assertFalse(m[0] > m[2])
        self.assertFalse(m[1] > m[1])
        self.assertFalse(m[2] > m[0])
        self.assertFalse(m[2] > m[1])

    def test_reachable(self):
        m = self.m
        self.assertTrue(m[0] >> m[1])
        self.assertTrue(m[0] >> m[0])
        self.assertTrue(m[1] >> m[2])
        self.assertTrue(m[1] >> m[0])
        self.assertTrue(m[2] >> m[2])
        self.assertTrue(m[0] >> m[2])
        self.assertTrue(m[1] >> m[1])
        self.assertFalse(m[2] >> m[0])
        self.assertFalse(m[2] >> m[1])
