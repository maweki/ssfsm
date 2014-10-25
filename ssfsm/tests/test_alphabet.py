from unittest import TestCase

import ssfsm

class TestAlphabet(TestCase):
    m = None

    def setUp(self):
        m = ssfsm.Machine()
        m.One['a'] = m.Two
        m().reset(m.One)
        self.m = m

    def test_large_polyfill(self):
        m = self.m
        m().alphabet = 'abcdefgh'
        for l in 'abcdefgh':
            self.assertIn(l, m().alphabet)
        for l in m().alphabet:
            self.assertIn(l, 'abcdefgh')
        self.assertRaises(KeyError, m, 'f')
        m().polyfill()
        m('f')
        self.assertRaises(KeyError, m, 'j')
