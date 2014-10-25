from unittest import TestCase

import ssfsm

class TestWith(TestCase):
    m = None

    def setUp(self):
        m = ssfsm.Machine()
        m.One['ab'] = m.Two
        m.Two['a'] = m.One
        m.Two['b'] = m.Two
        m().reset(m.One)
        self.m = m

    def test_deepcopy(self):
        from copy import deepcopy
        copy = deepcopy(self.m)
        self.assertIsNot(self.m, copy)
        self.assertIsInstance(copy, ssfsm.FSM_Machine)
        for state in self.m().states:
            self.assertIn(state.name, copy)
        for state in copy().states:
            self.assertIn(state.name, self.m)
