from unittest import TestCase

import ssfsm

class TestBasicSyntax(TestCase):
    m = None

    def setUp(self):
        self.m = ssfsm.Machine()

    def test_new_state(self):
        _ = self.m.newState

    def test_new_state_in_machine(self):
        _ = self.m.newState
        self.assertIn('newState', self.m)

    def test_new_state_gettable(self):
        s = self.m.newState
        self.assertEqual(s, self.m.newState)

    def test_simple_transition(self):
        self.m.Start['a'] = self.m.End
        self.m().reset(self.m.Start)
        self.assertEqual(self.m().state, self.m.Start)
        self.m('a')
        self.assertEqual(self.m().state, self.m.End)

    def test_machine_callable(self):
        self.m()

    def test_machine_length(self):
        self.assertEqual(0, len(self.m))
        _ = self.m.One
        self.assertEqual(1, len(self.m))
        _ = self.m.Two
        self.assertEqual(2, len(self.m))
        del self.m.One
        self.assertEqual(1, len(self.m))

    def test_state_accepting(self):
        self.m.One = True
        self.assertTrue(self.m.One.accepting)
        self.m.One = False
        self.assertFalse(self.m.One.accepting)
        with self.assertRaises(TypeError):
            self.m.One = 'Err'
        with self.assertRaises(TypeError):
            self.m.One.accepting = 'Err'

    def test_state_deletable(self):
        self.m.One = True
        self.assertIn('One', self.m)
        del self.m.One
        self.assertNotIn('One', self.m)
        with self.assertRaises(KeyError):
            del self.m.One

    def test_states_in_different_machines(self):
        m1 = ssfsm.Machine()
        m2 = ssfsm.Machine()
        with self.assertRaises(ValueError):
            m1.One['a'] = m2.Two

    def test_transition_target_is_state(self):
        with self.assertRaises(TypeError):
            self.m.One['a'] = 'err'

    def test_no_init_gives_error(self):
        m = self.m
        m.One = True
        m.One['a'] = m.One
        self.assertRaises(ValueError, m, 'a')
        m().reset(m.One)
        m('a')

    def test_state_access(self):
        m = self.m
        m.One
        self.assertIn('One', m)
        self.assertIs(m['One'], m.One)

        del m['One']

        m['One']
        self.assertIn('One', m)
        self.assertIs(m['One'], m.One)
