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
        self.assertIsInstance(state, ssfsm.DFA_State)

    def test_controller_calling(self):
        m = self.m
        m().reset(m.One)
        self.assertIs(m()(), m.One)
        self.assertIs(m(()), m.One)

    def test_controller_initial_state(self):
        m = self.m
        m().reset(m.One)
        self.assertIs(m.One, m().initial_state)

    def test_controller_initial_state_settable(self):
        m = self.m
        m().reset(m.One)
        m.Two
        self.assertIs(m.One, m().initial_state)
        m().initial_state = m.Two
        self.assertIs(m.Two, m().initial_state)

        with self.assertRaises(TypeError):
            m().initial_state = False

        m2 = ssfsm.Machine()
        m2.Foo
        with self.assertRaises(ValueError):
            m().initial_state = m2.Foo

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

    def test_remove_unreachable(self):
        m = self.m
        m.A['ab'] = m.B
        m.B['a'] = m.B
        m.B['b'] = m.A
        m().reset(m.A)
        self.assertEqual(len(m), 2)
        m().remove_unreachable_states()
        self.assertEqual(len(m), 2)
        m.C['ab'] = m.A
        self.assertEqual(len(m), 3)
        m().remove_unreachable_states()
        self.assertEqual(len(m), 2)
