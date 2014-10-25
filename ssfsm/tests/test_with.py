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

    def test_with_basic(self):
        m = self.m
        with m as _:
            pass

    def test_with_is_copy(self):
        m = self.m
        with m as copy:
            self.assertIsNot(m, copy)
            self.assertIsInstance(copy, ssfsm.FSM_Machine)
            for state in m().states:
                self.assertIn(state.name, copy)
            for state in copy().states:
                self.assertIn(state.name, m)

    def test_with_copy_behaviour(self):
        import itertools
        m = self.m
        for c in range(10):
            for p in itertools.product('ab', repeat=c):
                m().reset()
                with m as copy:
                    m(p)
                    copy(p)
                    self.assertEqual(m().state.name, copy().state.name)

    def test_with_alphabet(self):
        with self.m as copy:
            self.assertEqual(self.m().alphabet, copy().alphabet)
        self.m().alphabet = 'abc'
        with self.m as copy:
            self.assertEqual(self.m().alphabet, copy().alphabet)
        self.m().alphabet = 'a'
        with self.m as copy:
            self.assertEqual(self.m().alphabet, copy().alphabet)
