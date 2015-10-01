from unittest import TestCase
from common import all_words

import ssfsm

class TestMachineOperators(TestCase):
    m = None

    def setUp(self):
        m = ssfsm.Machine()
        self.m = m

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
        m_ = ~neg
        for word in all_words(m().alphabet, 10):
            with m as copy_m, neg as copy_neg, m_ as copy_m_:
                copy_m(word)
                copy_m_(word)
                copy_neg(word)
                self.assertIsNot(bool(copy_m), bool(copy_neg))
                self.assertIs(bool(copy_m), bool(copy_m_))
                check = 0 == ((len(word) - sum(word)) % 2)
                self.assertIs(bool(copy_m), bool(check))

        self.assertEqual(len(m), len(neg))

    def test_combine(self):
        A = ssfsm.Machine(0) # A is empty or ends with b
        A[0] = True
        A[0]['b'] = A[0]
        A[0]['a'] = A[1]
        A[1]['a'] = A[1]
        A[1]['b'] = A[0]

        def fn_A(w):
            w = ''.join(w)
            return (w == '') or (w[-1] == 'b')

        B = ssfsm.Machine(0) # B has aa
        B[0]['a'] = B[1]
        B[0]['b'] = B[0]
        B[1]['a'] = B[2]
        B[1]['b'] = B[0]
        B[2] = True
        B[2]['ab'] = B[2]

        def fn_B(w):
            w = ''.join(w)
            return 'aa' in w

        union = A | B
        intersection = A & B
        difference = A - B
        difference2 = B - A
        sym_diff = A ^ B

        from itertools import product

        for word in all_words(A().alphabet, 10):
            print(word)
            with A as copy_A, B as copy_B, union as copy_union:
                copy_A(word)
                copy_B(word)
                copy_union(word)
                cond = bool(copy_A) or bool(copy_B)
                cond2 = bool(copy_A | copy_B)
                cond3 = bool(copy_union)
                self.assertEqual(cond, cond2)
                self.assertEqual(cond, cond3)
                self.assertEqual(cond, fn_A(word) or fn_B(word))

            with A as copy_A, B as copy_B, intersection as copy_intersection:
                copy_A(word)
                copy_B(word)
                copy_intersection(word)
                cond = (bool(copy_A) and bool(copy_B))
                cond2 = bool(copy_A & copy_B)
                cond3 = bool(copy_intersection)
                self.assertEqual(cond, cond2)
                self.assertEqual(cond, cond3)
                self.assertEqual(cond, fn_A(word) and fn_B(word))

            with A as copy_A, B as copy_B, difference as copy_difference:
                copy_A(word)
                copy_B(word)
                copy_difference(word)
                cond = bool(copy_A) and not bool(copy_B)
                cond2 = bool(copy_A - copy_B)
                cond3 = bool(copy_difference)
                self.assertEqual(cond, cond2)
                self.assertEqual(cond, cond3)
                self.assertEqual(cond, fn_A(word) and not fn_B(word))

            with A as copy_A, B as copy_B, difference2 as copy_difference2:
                copy_A(word)
                copy_B(word)
                copy_difference2(word)
                cond = bool(copy_B) and not bool(copy_A)
                cond2 = bool(copy_B - copy_A)
                cond3 = bool(copy_difference2)
                self.assertEqual(cond, cond2)
                self.assertEqual(cond, cond3)
                self.assertEqual(cond, fn_B(word) and not fn_A(word))

            with A as copy_A, B as copy_B, sym_diff as copy_sym_diff:
                copy_A(word)
                copy_B(word)
                copy_sym_diff(word)
                cond = bool(copy_A) ^ bool(copy_B)
                cond2 = bool(copy_A ^ copy_B)
                cond3 = bool(copy_sym_diff)
                self.assertEqual(cond, cond2)
                self.assertEqual(cond, cond3)
                self.assertEqual(cond, (fn_A(word) or fn_B(word)) and not (fn_A(word) and fn_B(word)))

        max_len = len(A)*len(B)
        self.assertTrue(len(union) <= max_len)
        self.assertTrue(len(intersection) <= max_len)
        self.assertTrue(len(difference) <= max_len)
        self.assertTrue(len(difference2) <= max_len)
        self.assertTrue(len(sym_diff) <= max_len)

    def test_multi_alph(self):
        A = ssfsm.Machine(0) # A is empty or ends with b
        A[0] = True
        A[0][('bb',)] = A[0]
        A[0][('aa',)] = A[1]
        A[1][('aa',)] = A[1]
        A[1][('bb',)] = A[0]

        B = ssfsm.Machine(0) # B has aa
        B[0][('aa',)] = B[1]
        B[0][('bb',)] = B[0]
        B[1][('aa',)] = B[2]
        B[1][('bb',)] = B[0]
        B[2] = True
        B[2][('aa','bb')] = B[2]

        self.assertEqual((A & B)().alphabet, A().alphabet)

    def test_concatenation(self):
        import re
        B = ssfsm.Machine(0) # B has aa
        B[0]['a'] = B[1]
        B[0]['b'] = B[0]
        B[1]['a'] = B[2]
        B[1]['b'] = B[0]
        B[2] = True
        B[2]['ab'] = B[2]

        cat = B + B

        self.assertTrue(len(cat) <= len(B) + 2**len(B))
        fitting_regex = r"^.*(aa)+.*(aa).*$"

        for word in all_words(B().alphabet, 10):
            with cat as cat_copy:
                cat_copy(word)
                self.assertEqual(bool(cat_copy),bool(re.match(fitting_regex, ''.join(word))))

        from itertools import islice
        cat_neg = ~cat
        for word in islice(cat().language, 10000):
            self.assertIsNot(None, re.match(fitting_regex, ''.join(word)))

        for word in islice(cat_neg().language, 10000):
            self.assertIs(None, re.match(fitting_regex, ''.join(word)))


    def test_error_det(self):
        A = ssfsm.Machine(0)
        A[0]['ab'] = A[1]
        A[1]['a'] = A[0]

        B = ssfsm.Machine(0)
        B[0]['ab'] = B[1]
        B[1]['ab'] = B[0]

        with self.assertRaises(ValueError):
            A & B

    def test_error_alph(self):
        A = ssfsm.Machine(0)
        A[0]['ab'] = A[1]
        A[1]['ab'] = A[0]

        B = ssfsm.Machine(0)
        B[0]['abc'] = B[1]
        B[1]['abc'] = B[0]

        with self.assertRaises(ValueError):
            A & B

        with self.assertRaises(ValueError):
            A | B

        with self.assertRaises(ValueError):
            A ^ B

        with self.assertRaises(ValueError):
            A - B

        with self.assertRaises(ValueError):
            A + B

    def test_minimization(self):
        from itertools import takewhile
        try:
            from itertools import izip
            _zip = izip
        except:
            _zip = zip

        B = ssfsm.Machine(0) # B has aa
        B[0]['a'] = B[1]
        B[0]['b'] = B[0]
        B[1]['a'] = B[2]
        B[1]['b'] = B[0]
        B[2] = True
        B[2]['ab'] = B[2]

        C = B + B + B + B
        C_ = C().get_minimized()

        self.assertTrue(len(C_) <= len(C))
        self.assertTrue(C_().minimized)
        self.assertEqual(C().alphabet, C_().alphabet)

        # languages are equal
        for w1, w2 in takewhile(lambda x: len(x[0]) < 16, _zip(C().language, C_().language)):
            self.assertEqual(w1, w2)

        # state is retained
        for word in all_words(B().alphabet, 12):
            C().reset()
            C(word)
            C_ = C().get_minimized()
            n1, n2 = C().state.name, C_().state.name
            self.assertTrue((n1 == n2) or (n1 in n2), "Unequivalent states for {}, {} <-> {}".format(word, n1, n2))
            self.assertIs(bool(C), bool(C_))
