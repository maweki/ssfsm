# ssfsm - Stupidly Simple Finite State Machines

ssfsm is a constructive library implementing deterministic finite state machines
(currently only deterministic finite automaton - DFAs).
The fun thing is, that it has a stupidly simple API.

## Installation
`pip install ssfsm`

https://pypi.python.org/pypi/ssfsm/


## Usage
A full documentation is in the works and you can look at some examples
in the tests-directory but here are a few ideas on how the library works:


### Basic construction of DFAs
```
# A DFA that accepts b*a(ab)*
import ssfsm
A = ssfsm.Machine()
A.One['a'] = A.Two
A.One['b'] = A.One
A.Two['ab'] = A.Two # a and b transition
A.Two = True # Set state Two to accepting
A().reset(A.One)
```
The initial state needs to be set with `A().reset(A.One)`.
You can also create an initial state with the constructor like `A = ssfsm.Machine('One')`.

States can be deleted with the **del** statement
```
A().states # frozenset({<ssfsm.FSM_State object>, <ssfsm.FSM_State object>})
del A.Two
A().states # frozenset({<ssfsm.FSM_State object>})
```
Their transitions (and the transitions leading to them) will be removed as well.

### Transitions
Transitions are executed by calling the machine with the transition.
```
A('a') # a-Transition
A('ab') # a-Transition followed by b-Transition
```

The current state after the last transition is returned. Because of the order of execution, `Machine('a') is Machine().state` is True (given the transition exists) while `Machine().state is Machine('a')` may not be.

### Accepting
When cast to boolean, we see whether the DFA is in an accepting state
or not.
```
A('baab')
if A:
  # baab is an accepted word
else:
  # it is not
```

### Polyfill
Constructing DFAs, even with a nice syntax, can be tedious. So here is
polyfill:
```
A = ssfsm.Machine()
A.One['a'] = A.Two
A().alphabet = 'ab'
A().polyfill() # all remaining transitions are filled, to stay in the same state
```
You also can call polyfill() with a parameter to set all remaining
transitions to a specific state like `A().polyfill(A.Two)`.

The `A().alphabet` is determined by all the transitions that are defined.
If you've allready defined your whole alphabet via the transitions, this
is not neccessary. But for polyfill-usage, you can set an alphabet. This
also deletes transitions that are not part of the alphabet.

```
A = ssfsm.Machine()
A.One['c'] = A.Two
A.One.transitions # frozenset({'c'})
A().alphabet = 'ab'
A.One.transitions # frozenset()
```

### with/copy
If you've painstakenly created a DFA and want to use it but, after usage,
want to return to a previous state, you can use the **with** statement.

```
A = ssfsm.Machine()
# create all states and transitions
with A as A_copy:
  A_copy('a') # a-transition only in A_copy
```

Both copies are not considered equal and have disjunct states.

A machine also supports the copy/deepcopy api, which is used for the
with-statement.

### Decorators

You can add decorators to functions so that with each function call,
a transition in the machine is executed.

```
A = ssfsm.Machine()
# create all states and transitions

@ssfsm.emmit(A, 'a')
def foo():
  pass

foo() # the same as A('a')
```

The transition happens before the function is called so
that the function will observe the new state of the machine.

If you want the transition to happen after the actual function
call and observe the previous state, you can use the decorator `emmit_after`. `emmit_before`
is an alias for `emmit`.

### Machine operations

`~Machine` returns a negated copy of the Machine. The current and initial state
of the negated copy are the current and initial state of the original Machine.

`MachineA - MachineB` returns a DFA that has all the accepting words of A
without those of B (difference). Both DFAs need to be deterministic. Both DFAs
need to have the same alphabet.

`MachineA & MachineB` returns a DFA that has all the accepting words of A
that are also accepting words of B (intersection). Both DFAs need to be
deterministic. Both DFAs need to have the same alphabet.

`MachineA | MachineB` returns a DFA that has all the accepting words of A
and all accepting words of B (union). Both DFAs need to be deterministic. Both
DFAs need to have the same alphabet.

`MachineA ^ MachineB` returns a DFA that has all the accepting words of A
and all accepting words of B that are not accepting words of A and B (symmetric difference).
Both DFAs need to be deterministic. Both DFAs need to have the same alphabet.

For the operations `-`, `&`, `|` and `^`, the resulting machine has (as its states)
the cross-product of the states of the original DFAs. The machine is not minimized
(so it may have redundant and unreachable states).

`MachineA + MachineB` returns a DFA that has the concatenation of the languages
of A and B so that the language of A + B is every word accepted by A concatenated
with every word accepted by B.

For the operation `+` the states of the resulting machine have as their names
a tuple where the first part is a state from A and the second part is a frozenset
of states from B (or an empty set).

### Information about machines

`len(Machine)` returns the number of states in the machine

`Machine().state` is the current state. *writable*

`Machine().initial_state` is the initial state. *writable*

`Machine().states` is the set of states

`Machine().transitions` returns the set of transitions as a three-tuple of *(from, transition, to)* representing the state-transition function as a set.

`Machine().alphabet` is the set of transitions/the alphabet of the machine. *writable*

`Machine().deterministic` is True when the machine is deterministic so that for every transition in the alphabet, every state in the machine has that transition and an inital state is defined.

`Machine().reachable_states` is the set of states reachable from the initial state
(the empty set, if no inital state is set)

`Machine().accepting_states` is the set of states that are accepting

`Machine().infinite_language` and `Machine().finite_language` whether the by the
automaton described language is finite or infinite.

`Machine().get_pumping_lemma()` returns a triple u,v,w so that any u v* w is in
the language of the automaton. This triple can be used to show, that the language
is infinite, using the pumping lemma. If the language is finite, this method
returns *None*.

`Machine().language` returns a generator of all words of the language (as tuples
of increasing length). The language might be infinite. The words are yielded with
increasing length. If the alphabet can be sorted, words of the same length will
be yielded in lexicographical order.

`Machine().regular_language` returns True, if the language described by the DFA
is a regular language.

`Machine().remove_unreachable_states()` removes all states of the machine that
are not reachable from the initial state.

`Machine().dot` is the string representing the machine as a dot-graph.

**If you don't like the `Machine()`-syntax** to access the FSM, you can use the alternate syntax `Machine._.alphabet` and so on.

### Information about states

`state.name` is the name of the state.

`state.parent` is the DFA the state is in.

`state.transitions` is the set of transitions the state has.

`state.following` is the set of states directly reachable via the transitions (1 step)

`state.reachable` is the set of states reachable via the transitions (1 or more steps)

`state.accepting` whether the state is an accepting state. *writable*

`a in state` whether a is a transition of the state.

`state1 > state2` whether `state2` is directly reachable from `state1` (equivalent
  to `state2 in state1.transitions`)

`state1 >> state2` whether `state2` is reachable from `state1` (equivalent
  to `state2 in state1.reachable`)

### Programmatic quirks and implementation details

States can be accessed via the dot-operator as `Machine.State`.
If you want to access states programmatically or want different
qualifiers as state-names, you can also access them via `Machine[State]`.
Therefore if A is a `Machine`, `A.One` and `A['One']` are equivalent.
Whereas the state `A[1]` or `A[('Foo', 'Bar')]` can not be created or
accessed via the dot-operator.

A state is created when it is first accessed. Therefore a plain
statement can have observable side-effects.
```
A = ssfsm.Machine()
'foo' in A # False
A.foo # plain expression with side-effects
'foo' in A # True
```

Using `Machine.State = True` to set a state to accepting is syntactic
sugar and is **not equal** to `f = Machine.State; f = True`. If you want
to do something like that, the syntax is `f = Machine.State; f.accepting = True`.
The accepting-property can also be read.

States and transitions are kept in dictionaries, therefore a
state-identifier as well as all transitions need to be hashable.

Transitions are checked for iterability and if they are iterable, they are iterated over and the transitions are applied/created in order. Therefore `Machine.State[''] = Machine.OtherState` will not create a transition, neither will `Machine('')` apply a transition.

`Machine()()`, is like an empty transition and therefore an
alias to `Machine().state` or `Machine(())` or `Machine('')`

Due to how the **del** statement works, `del m.A` is not equivalent to `a = m.A; del a`.
The latter does only remove the reference `a` from the frame and not the A-state
from the machine.

## Unit tests

Just run `nosetests` from within the project directory. The test-coverage (`nosetests --with-coverage --cover-erase`) should be quite high.

## Further Work
In the future I want to do:
* more tests
* nondeterministic FAs
* a nice documentation
* more decorators to control program flow
* Minimization (removing unused states, reduce redundant states)
* other finite state machines than DFAs

## License

This library is licensed under GPL 2.0
