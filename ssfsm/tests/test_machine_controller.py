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
