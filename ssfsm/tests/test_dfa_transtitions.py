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

    def test_execution_order(self):
        m = self.m
        self.assertIs(m('a'), m().state)
        m().reset(m.One)
        self.assertIsNot(m().state, m('a'))

    def test_non_alphabet(self):
        self.assertRaises(KeyError, self.m, 'c')
        self.assertRaises(KeyError, self.m, 'cdefg')

    def test_error(self):
        self.assertNotIn('c', self.m.One)
        self.assertRaises(KeyError, self.m, 'c')

    def test_delete_transition(self):
        self.assertIn('b', self.m.One)
        del self.m.One['b']
        self.assertNotIn('b', self.m.One)

    def test_delete_state(self):
        self.assertIn('One', self.m)
        self.assertIn('a', self.m.Two)
        del self.m.One
        self.assertNotIn('a', self.m.Two)

    def test_accepting(self):
        m = self.m
        m.Three = True
        self.assertFalse(m)
        self.assertFalse(m().accepting)
        m('aa')
        self.assertFalse(m)
        self.assertFalse(m().accepting)
        m('ab')
        self.assertTrue(m)
        self.assertTrue(m().accepting)

    def test_returned_state(self):
        m = self.m
        self.assertIs(m('a'), m.Two)

    def test_set_state(self):
        m = self.m
        self.assertIs(m().state, m.One)
        m().state = m.Two
        self.assertIs(m().state, m.Two)
        with self.assertRaises(TypeError):
            m.state = 'err'
