from unittest import TestCase

import ssfsm

class TestBasicSyntax(TestCase):
    def test_constructor_module(self):
        ssfsm.Machine()

    def test_constructor_machine(self):
        ssfsm.DFA_Machine()

    def test_constructor_machine_with_initial(self):
        A = ssfsm.DFA_Machine('foo')
        self.assertIn('foo', A)
        self.assertIs(A().state, A.foo)

    def test_constructor_state(self):
        ssfsm.DFA_State(ssfsm.DFA_Machine(), 'foo')
