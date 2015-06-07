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

### Information about machines

`len(Machine)` returns the number of states in the machine

`Machine().state` is the current state. *writable*

`Machine().initial_state` is the initial state.

`Machine().states` is the set of states

`Machine().transitions` returns the set of transitions as a three-tuple of *(from, transition, to)* representing the state-transition function as a set.

`Machine().alphabet` is the set of transitions/the alphabet of the machine. *writable*

`Machine().deterministic` is True when the machine is deterministic so that for every transition in the alphabet, every state in the machine has that transition and an inital state is defined.

**If you don't like the `Machine()`-syntax** to access the FSM, you can use the alternate syntax `Machine._.alphabet` and so on.

### Information about states

`state.name` is the name of the state.

`state.parent` is the DFA the state is in.

`state.transitions` is the set of transitions the state has.

`state.accepting` whether the state is an accepting state. *writable*

`a in state` whether a is a transition of the state.


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

## Unit tests

Just run `nosetests` from within the project directory. The test-coverage (`nosetests --with-coverage --cover-erase`) should be quite high.

## Further Work
In the future I want to do:
* more tests
* nondeterministic DFAs
* operations on DFAs (concatenation, union, intersection)
* a nice documentation
* more decorators to control program flow
* Minimization (removing unused states, reduce redundant states)
* dot output
* other finite state machines than DFAs

## License

This library is licensed under GPL 2.0
