from unittest import TestCase
from common import all_words
import ssfsm

class TestMachineOperators(TestCase):
    m = None

    def setUp(self):
        A = ssfsm.Machine(0) # A is empty or ends with b
        A[0] = True
        A[0]['b'] = A[0]
        A[0]['a'] = A[1]
        A[1]['a'] = A[1]
        A[1]['b'] = A[0]
        self.A = A

        B = ssfsm.Machine(0) # B has aa
        B[0]['a'] = B[1]
        B[0]['b'] = B[0]
        B[1]['a'] = B[2]
        B[1]['b'] = B[0]
        B[2] = True
        B[2]['ab'] = B[2]
        self.B = B

    def test_regularity(self):
        self.assertTrue(self.A().regular_language)

    def test_pumping_lemma_positive(self):
        from itertools import product

        machines = [self.A, self.B]
        for m, star in product(machines, range(50)):
            with m as m_copy:
                u, v, w = m_copy().get_pumping_lemma()
                word = u + v*star + w
                m_copy(word)
                self.assertTrue(m_copy)

    def test_language(self):
        from itertools import takewhile
        l = 10

        machines = [self.A, self.B]
        for m in machines:
            self.assertTrue(m().infinite_language)
            self.assertFalse(m().finite_language)
            words = frozenset(all_words(m().alphabet, l))
            accepted_by_machine = frozenset(takewhile(lambda x: len(x) <= l, m().language))
            for word in words:
                with m as m_copy:
                    m_copy(word)
                    self.assertEqual(bool(m_copy), word in accepted_by_machine)

    def test_language_empty(self):
        A = ssfsm.Machine(0)
        A[0]['ab'] = A[1]
        A[1]['ab'] = A[0]
        self.assertFalse(next(A().language, False))
        self.assertIs(None, A().get_pumping_lemma())
        self.assertTrue(A().finite_language)
        self.assertFalse(A().infinite_language)

    def test_language_empty_word(self):
        A = ssfsm.Machine(0)
        A[0]['ab'] = A[1]
        A[1]['ab'] = A[1]
        A[0] = True
        language = frozenset(A().language)
        language_expected = {()}
        self.assertEqual(language, language_expected)
        self.assertIs(None, A().get_pumping_lemma())
        self.assertTrue(A().finite_language)
        self.assertFalse(A().infinite_language)
