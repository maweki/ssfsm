from unittest import TestCase

import ssfsm

class TestTransitions(TestCase):
    m = None

    def setUp(self):
        m = ssfsm.Machine()
        m.One['a'] = m.Two
        m.Two['a'] = m.One
        m.One['b'] = m.Three
        m().polyfill(m.Three)
        m().reset(m.One)
        self.m = m

    def test_simple_transition(self):
        m = self.m
        self.assertIs(m().state, m.One)
        m('a')
        self.assertIs(m().state, m.Two)
        m('a')
        self.assertIs(m().state, m.One)
        for _ in range(10):
            m('b')
            self.assertIs(m().state, m.Three)

    def test_multi_transition(self):
        m = self.m
        self.assertIs(m().state, m.One)
        m('aaa')
        self.assertIs(m().state, m.Two)
        m('bbbbbbbbbbbbbbbbb')
        self.assertIs(m().state, m.Three)

    def test_non_alphabet(self):
        self.assertRaises(KeyError, self.m, 'c')
        self.assertRaises(KeyError, self.m, 'cdefg')
