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

    def test_reset(self):
        m = self.m
        self.assertIs(m().state, m.One)
        m('a')
        self.assertIs(m().state, m.Two)
        m().reset()
        self.assertIs(m().state, m.One)
        m().reset(m.Two)
        self.assertIs(m().state, m.Two)
        m('a')
        self.assertIs(m().state, m.One)
        with self.assertRaises(ValueError):
            m().reset(ssfsm.Machine().s)

    def test_str(self):
        m = self.m
        self.assertEqual(str(m.One), '<state.One>')
        self.assertEqual(str(m['two']), '<state.two>')
        self.assertEqual(str(m[1]), '<state.1>')

    def test_alternate_controller_syntax(self):
        m = self.m
        c1 = m._
        c2 = m()
        self.assertIs(c1.parent, c2.parent)
