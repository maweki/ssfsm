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
