from unittest import TestCase

import ssfsm

class TestDecorators(TestCase):
    m = None

    def setUp(self):
        m = ssfsm.Machine()
        m.One['ab'] = m.Two
        m.Two['a'] = m.One
        m.Two['b'] = m.Two
        m().reset(m.One)
        self.m = m

    def test_emmit(self):
        m = self.m

        @ssfsm.emmit(m, "a")
        def testfunc(arg):
            self.assertEquals(arg, "TestVal")
            return "Return"

        self.assertIs(m().state, m.One)
        self.assertEqual(testfunc("TestVal"), "Return")
        self.assertIs(m().state, m.Two)
        self.assertEqual(testfunc("TestVal"), "Return")
        self.assertIs(m().state, m.One)
