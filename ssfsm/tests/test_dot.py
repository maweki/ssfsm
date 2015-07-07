from unittest import TestCase

import ssfsm

class TestDotConstructorTest(TestCase):
    # these all shouldn't throw exceptions

    def test_dot_constructor(self):
        cases = [
            ('ab', 'a', 'b'),
            ((1,2), 1, 2),
            ((True,False), True, False),
            (("foo","bar"), "foo", "bar")
        ]

        statenames = [
            ('One', 'Two'),
            (1, 2),
            (True, False)
        ]

        asssertion = 'digraph'

        from itertools import product

        for case, states in product(cases, statenames):
            print(case, states)
            A = ssfsm.Machine()
            self.assertIn(asssertion, A().dot)
            A[states[0]][case[0]] = A[states[0]]
            self.assertIn(asssertion, A().dot)
            A[states[1]][case[1]] = A[states[0]]
            self.assertIn(asssertion, A().dot)
            A[states[1]][case[2]] = A[states[1]]
            self.assertIn(asssertion, A().dot)
            A[states[1]] = True
            self.assertIn(asssertion, A().dot)
            A().reset(A[states[0]])
            self.assertIn(asssertion, A().dot)
