from unittest import TestCase

import ssfsm

class TestMachineController(TestCase):
    m = None

    def setUp(self):
        self.m = ssfsm.Machine()

    def test_states_empty(self):
        self.assertEqual(len(self.m().states),0)

    def test_states_create(self):
        state = self.m.TestState
        self.assertIn('TestState', self.m().states_names)
        self.assertIn(state, self.m().states)
        self.assertIsInstance(state, ssfsm.FSM_State)

    def test_controller_calling(self):
        m = self.m
        m().reset(m.One)
        self.assertIs(m()(), m.One)
        self.assertIs(m(()), m.One)

    def test_transitions(self):
        m = self.m
        self.assertEqual(m().transitions, frozenset())
        m.One[0] = m.Two
        m.One[1] = m.One
        m().polyfill()
        ts = m().transitions
        self.assertEqual(len(ts),4)
        self.assertIn((m.One, 0, m.Two) ,ts)
        self.assertIn((m.One, 1, m.One) ,ts)
        self.assertIn((m.Two, 0, m.Two) ,ts)
        self.assertIn((m.Two, 1, m.Two) ,ts)

    def test_deterministic(self):
        m = self.m
        m().reset(m.One)
        print(m().states_names)
        m.One['ab'] = m.Two
        self.assertFalse(m().deterministic)
        m.Two['a'] = m.One
        self.assertFalse(m().deterministic)
        m.Two['b'] = m.Two
        self.assertTrue(m().deterministic)
        m.One['c'] = m.One
        self.assertFalse(m().deterministic)

        m = ssfsm.Machine()
        m.One['ab'] = m.Two
        self.assertFalse(m().deterministic)
        m.Two['a'] = m.One
        self.assertFalse(m().deterministic)
        m.Two['b'] = m.Two
        self.assertFalse(m().deterministic)
        m().reset(m.One)
        self.assertTrue(m().deterministic)
