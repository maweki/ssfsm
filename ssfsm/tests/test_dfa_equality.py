from unittest import TestCase

import ssfsm

class TestEquality(TestCase):
    m1 = None

    def setUp(self):
        m = ssfsm.Machine()
        m.One['ab'] = m.Two
        m.Two['a'] = m.One
        m.Two['b'] = m.Two
        m().alphabet = 'abc'
        self.m1 = m

        m = ssfsm.Machine()
        m.One['ab'] = m.Two
        m.Two['a'] = m.One
        m.Two['b'] = m.Two
        m().alphabet = 'abc'
        self.m2 = m

    def test_machine_equality(self):
        with self.assertRaises(NotImplementedError):
            self.assertEqual(self.m1, self.m1)
            self.assertEqual(self.m1, self.m2)
