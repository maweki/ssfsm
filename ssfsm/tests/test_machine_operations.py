from unittest import TestCase

import ssfsm

class TestMachineOperators(TestCase):
    m = None

    def setUp(self):
        m = ssfsm.Machine()
        self.m = m

    @staticmethod
    def all_words(alphabet, upto):
        from itertools import product
        for length in range(upto + 1):
            for word in product(alphabet, repeat=length):
                yield word

    def test_negate(self):
        # finite-state machine that determines whether a binary number has an even number of 0s (wikipedia example)
        m = self.m
        m().reset(m.S1)
        m().alphabet = (0,1)
        m.S1[0] = m.S2
        m.S2[0] = m.S1
        m().polyfill()
        m.S1 = True

        neg = ~m # odd number of 0s
        for word in self.all_words(m().alphabet, 10):
            with m as copy_m, neg as copy_neg:
                copy_m(word)
                copy_neg(word)
                self.assertIsNot(bool(copy_m), bool(copy_neg))
                check = 0 == ((len(word) - sum(word)) % 2)
                self.assertIs(bool(copy_m), bool(check))

        self.assertEqual(len(m), len(neg))
