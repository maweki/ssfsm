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

    def test_emmit_before(self):
        m = self.m

        @ssfsm.emmit(m, "a")
        def testfunc(arg):
            self.assertIs(m().state, m.Two)
            self.assertEquals(arg, "TestVal")
            return "Return"

        self.assertIs(m().state, m.One)
        self.assertEqual(testfunc("TestVal"), "Return")
        self.assertIs(m().state, m.Two)

    def test_emmit_after(self):
        m = self.m

        @ssfsm.emmit_after(m, "a")
        def testfunc(arg):
            self.assertIs(m().state, m.One)
            self.assertEquals(arg, "TestVal")
            return "Return"

        self.assertIs(m().state, m.One)
        self.assertEqual(testfunc("TestVal"), "Return")
        self.assertIs(m().state, m.Two)
