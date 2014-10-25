from unittest import TestCase

import ssfsm

class TestPolyfill(TestCase):
    m = None

    def setUp(self):
        self.m = ssfsm.Machine()

    def test_polyfill_simple(self):
        m = self.m
        m.Start['ab'] = m.End
        m().polyfill()
        self.assertIn('a', m.End)
        self.assertIn('b', m.End)
        self.assertIs(m.End['a'], m.End)
        self.assertIs(m.End['b'], m.End)

    def test_polyfill_target(self):
        m = self.m
        m.Start['ab'] = m.End
        m().polyfill(m.Start)
        self.assertIn('a', m.End)
        self.assertIn('b', m.End)
        self.assertIs(m.End['a'], m.Start)
        self.assertIs(m.End['b'], m.Start)

    def test_polyfill_complex(self):
        m = self.m
        m.Start['a'] = m.End
        m.End['b'] = m.Start
        m().polyfill()
        for l in 'ab':
            for s in m().states:
                self.assertIn(l, s)
        self.assertIs(m.Start['b'], m.Start)
        self.assertIs(m.Start['a'], m.End)
        self.assertIs(m.End['a'], m.End)
        self.assertIs(m.End['b'], m.Start)
