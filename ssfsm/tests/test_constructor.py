from unittest import TestCase

import ssfsm

class TestBasicSyntax(TestCase):
    def test_constructor_module(self):
        ssfsm.Machine()

    def test_constructor_machine(self):
        ssfsm.FSM_Machine()

    def test_constructor_state(self):
        ssfsm.FSM_State(ssfsm.FSM_Machine(), 'foo')
