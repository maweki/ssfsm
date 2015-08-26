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
            self.assertIsInstance(copy, ssfsm.DFA_Machine)
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

    def test_with_multi_alphabet(self):
        m = ssfsm.Machine()
        m.One[('aa','bb')] = m.Two
        m.Two[('aa',)] = m.One
        m.Two[('bb',)] = m.Two
        m().reset(m.One)
        with m as m_:
            self.assertEqual(m().alphabet, m_().alphabet)

    def test_bug_state_not_retained(self):
        A = ssfsm.Machine(0) # A ends with b
        A[0]['b'] = A[1]
        A[0]['a'] = A[0]
        A[1]['b'] = A[1]
        A[1]['a'] = A[0]
        A[1] = True

        A = A+A
        A('b')
        with A as A_:
            self.assertEqual(A().state.name, A_().state.name)
