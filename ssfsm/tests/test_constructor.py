from unittest import TestCase

import ssfsm

class TestBasicSyntax(TestCase):
    def test_constructor_module(self):
        ssfsm.Machine()

    def test_constructor_machine(self):
        ssfsm.FSM_Machine()

    def test_constructor_machine_with_initial(self):
        A = ssfsm.FSM_Machine('foo')
        self.assertIn('foo', A)
        self.assertIs(A().state, A.foo)

    def test_constructor_state(self):
        ssfsm.FSM_State(ssfsm.FSM_Machine(), 'foo')
