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

    def test_state_accepting(self):
        self.m.One = True
        self.assertTrue(self.m.One.accepting)
        self.m.One = False
        self.assertFalse(self.m.One.accepting)

    def test_no_init_gives_error(self):
        m = self.m
        m.One = True
        m.One['a'] = m.One
        self.assertRaises(ValueError, m, 'a')
        m().reset(m.One)
        m('a')
