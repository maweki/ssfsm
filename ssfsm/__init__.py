r"""ssfsm is a finite-state-machine implementation with the most simple syntax
I could come up with."""

VERSION = "0.6.0"

def Machine(*nargs, **kwargs):
    """Returns a new :py:class:`FSM_Machine`"""
    return FSM_Machine(*nargs, **kwargs)

def require_determinism(func):
    from functools import wraps
    @wraps(func)
    def wrapper(*args):
        for arg in args:
            if (isinstance(arg, FSM_Machine) and not arg().deterministic) or (isinstance(arg, FSM_Machine_Controller) and not arg.deterministic):
                raise ValueError("One or all Machines are not deterministic")
        return func(*args)
    return wrapper

class FSM_Machine(object):
    """The machine"""

    __states = None
    __active_state = None
    __initial_state = None
    __alphabet = None

    def __init__(self, initial_state=None):
        self.__states = {}
        self.__alphabet = frozenset()
        if not (initial_state is None):
            self().reset(self[initial_state])

    def __get_state(self, name):
        if name in self:
            return self.__states[name]
        return self.__create_state(name)

    def __contains__(self, item):
        return item in self.__states

    def __len__(self):
        return len(self.__states)

    def __nonzero__(self):
        return bool(self.__active_state.accepting)

    def __bool__(self):
        return bool(self.__active_state.accepting)

    def __create_state(self, name):
        if name in self:
            raise ValueError("State allready created")
        new_state = FSM_State(self, name)
        self.__states[name] = new_state
        return new_state

    def __deepcopy(self):
        copy = FSM_Machine()
        copy().alphabet = self.__alphabet
        for key in self.__states:
            copy[key] = self.__states[key].accepting
        for key in self.__states:
            for transition in self.__states[key].transitions:
                copy[key][(transition,)] = copy[self.__states[key][transition].name]
        copy().reset(copy[self.__initial_state.name])
        copy().state = copy[self.__active_state.name]
        return copy

    def __deepcopy__(self, _):
        return self.__deepcopy()

    def __enter__(self):
        return self.__deepcopy()

    def __exit__(self, _type, value, traceback):
        pass

    def __eq__(self, other):
        raise NotImplementedError()

    def __call__(self, transition=None):
        if transition is None:
            return FSM_Machine_Controller(self)

        try:
            for t in transition:
                self.__change_state(self.__active_state(t))
        except TypeError:
            try:
                self.__change_state(self.__active_state(transition))
            except TypeError:
                raise ValueError('No State initialized. Set an initial state with Machine().reset(state).')
        return self().state

    def __change_state(self, state):
        if not state.parent is self:
            raise ValueError("States are not in the same machine")
        self.__active_state = state
        return state

    def __getitem__(self, key):
        if key == '_':
            return self()
        return self.__get_state(key)

    def __setitem__(self, key, value):
        self.__get_state(key).accepting = value

    def __delitem__(self, key):
        name = key
        if name in self:
            state = self.__states[name]
            if self.__active_state is state:
                self.__active_state = None
            del self.__states[name]
            for o_name in self.__states:
                self.__states[o_name].delete(state)
        else:
            raise KeyError('State doesn\'t exist in this machine')

    def __getattr__(self, name):
        return self[name]

    def __delattr__(self, name):
        del self[name]

    def __setattr__(self, name, value):
        if name.startswith('_'):
            return object.__setattr__(self, name, value)
        self[name] = value

    @require_determinism
    def __add__(self, other):
        if not self().alphabet == other().alphabet:
            raise ValueError("Alphabets are not equal")

        init_other_set = frozenset((other.__initial_state.name,))
        o_set = frozenset() if not self.__initial_state.accepting else init_other_set
        init_state = (self.__initial_state.name, o_set)
        queue = {init_state}

        new_machine = FSM_Machine(init_state)
        while queue:
            this_state = queue.pop()
            for a in self().alphabet:
                if this_state in new_machine and a in new_machine[this_state]:
                    continue
                self_state, other_states = this_state
                next_state_self = self[self_state][a].name
                next_state_other = frozenset(other[s][a].name for s in other_states)
                if self[next_state_self].accepting:
                    next_state_other |= init_other_set
                next_state = next_state_self, next_state_other
                new_machine[this_state][(a,)] = new_machine[next_state]
                queue.add(next_state)

        for state in new_machine().states:
            _, o = state.name
            state.accepting = any(other[s].accepting for s in o)

        return new_machine


    def __or__(self, other):
        from operator import or_
        return FSM_Machine.__cross_combine(self, other, or_)

    def __and__(self, other):
        from operator import and_
        return FSM_Machine.__cross_combine(self, other, and_)

    def __sub__(self, other):
        return FSM_Machine.__cross_combine(self, other, lambda a, b: a and not b)

    def __xor__(self, other):
        from operator import xor
        return FSM_Machine.__cross_combine(self, other, xor)

    @staticmethod
    @require_determinism
    def __cross_combine(first, second, accepting_operation):
        if not first().alphabet == second().alphabet:
            raise ValueError("Alphabets are not equal")

        from itertools import product
        new_machine = Machine()

        for f, s in product(first().states, second().states):
            # @TODO Improvement: do that constructively
            new_machine[(f.name,s.name)].accepting = accepting_operation(f.accepting, s.accepting)
            for a in first().alphabet:
                new_machine[(f.name,s.name)][(a,)] = new_machine[(f[a].name, s[a].name)]

        initial = (first().initial_state.name, second().initial_state.name)
        new_machine().reset(new_machine[initial])
        new_machine().state = new_machine[(first().state.name, second().state.name)]

        return new_machine

    def __invert__(self):
        with self as new_machine:
            for state in new_machine().states:
                state.accepting = not state.accepting
            return new_machine

    def __toDot(self, compress_frozenset=True, wrapwidth=15):
        from collections import defaultdict
        statements = []
        statements += [ 'rankdir=LR' ]
        statements += [ '0  [ style=invis ][ shape=point ]' ]

        nodes = dict((state, num) for num, state in enumerate(self.__states.values(), start=1)) # node -> its id
        for node in nodes:
            # register nodes
            shape = 'doublecircle' if node.accepting else 'circle'
            node_name = str(node.name)
            if compress_frozenset:
                from re import sub
                node_name = node_name.replace(str(frozenset()), '{}')
                node_name = sub(r"frozenset\((.+?)\)", (lambda match: match.group(1)), node_name)
            if wrapwidth:
                from textwrap import wrap
                node_name = "\\n".join(wrap(node_name, wrapwidth))
            statements += [ '%d [ shape=%s ][ label="%s" ]' % (nodes[node], shape, node_name) ]

        for from_node in nodes:
            # build edges
            collected_transitions = defaultdict(set) # to_node -> set of transitions
            for transition in from_node.transitions:
                collected_transitions[from_node[transition]].add(str(transition))

            for to_node in collected_transitions:
                sep = '' if all(len(str(t)) == 1 for t in collected_transitions[to_node]) else ', '
                statements += [ '%d -> %d [ label="%s" ]' % ( nodes[from_node], nodes[to_node], sep.join(sorted(collected_transitions[to_node])) ) ]

            if from_node is self.__initial_state:
                statements += [ '0 -> %d' % nodes[from_node] ]

        graph = 'digraph { stmt_list }'.replace('stmt_list', ';\n'.join(statements))
        return graph

class FSM_Machine_Controller(object):
    def __init__(self, parent):
        self.__parent = parent

    def __call__(self):
        # @TODO Is this the expected behaviour?
        return self.state

    @property
    def parent(self):
        return self.__parent

    @property
    def accepting(self):
        return bool(self.parent)

    @property
    def states(self):
        return frozenset(self.parent._FSM_Machine__states.values())

    @property
    def states_names(self):
        return frozenset(s.name for s in self.states)

    @property
    def state(self):
        return self.parent._FSM_Machine__active_state

    @state.setter
    def state(self, state):
        self.parent._FSM_Machine__change_state(state)

    @property
    def deterministic(self):
        from itertools import product
        return (self.initial_state in self.states) and all((trans in state) for (state, trans) in product(self.states, self.alphabet))

    @property
    def initial_state(self):
        return self.parent._FSM_Machine__initial_state

    @initial_state.setter
    def initial_state(self, state):
        if not isinstance(state, FSM_State):
            raise TypeError("Transition target must be a state")

        if state.parent is self.__parent:
            self.parent._FSM_Machine__initial_state = state
        else:
            raise ValueError("States are not in the same machine")

    @property
    def reachable_states(self):
        if (self.initial_state in self.states):
            return self.initial_state.reachable
        else:
            return frozenset()

    @property
    def accepting_states(self):
        return frozenset(s for s in self.states if s.accepting)

    @property
    def dot(self):
        return self.parent._FSM_Machine__toDot()

    def reset(self, initial_state=None):
        if initial_state is None:
            self.parent._FSM_Machine__change_state(self.initial_state)
        else:
            if initial_state.parent is self.parent:
                self.initial_state = initial_state
                self.reset()
            else:
                raise ValueError("States are not in the same machine")

    @property
    def alphabet(self):
        s = self.parent._FSM_Machine__alphabet
        for state in self.states:
            s = s | state.transitions
        return s

    @alphabet.setter
    def alphabet(self, val):
        to_delete = self.alphabet - frozenset(val)
        self.parent._FSM_Machine__alphabet = frozenset(val)
        for state in self.states:
            for d in to_delete:
                if d in state:
                    del state[d]

    @property
    def transitions(self):
        def __transitions():
            for fro in self.states:
                for trans in fro.transitions:
                    yield (fro, trans, fro[trans])
        return frozenset(__transitions())

    @require_determinism
    def remove_unreachable_states(self):
        for rem in self.states - self.reachable_states:
            del self.parent[rem.name]

    @property
    @require_determinism
    def infinite_language(self):
        return any(self.__get_infinite_language_states())

    def __get_infinite_language_states(self):
        # using pumping lemma
        from itertools import product
        reachable = self.reachable_states
        looping_states = (state for state in reachable if state >> state)
        return ((state, accepting) for state, accepting in product(looping_states, self.accepting_states & reachable) if state >> accepting)

    @require_determinism
    def get_pumping_lemma(self):
        for state, accepting in self.__get_infinite_language_states():
            prefix = () if self.initial_state is state else self.initial_state.path_to(state)
            suffix = () if state is accepting else state.path_to(accepting)
            return (prefix, state.path_to(state), suffix)
        return None

    @property
    def finite_language(self):
        return not self.infinite_language

    @property
    @require_determinism
    def regular_language(self):
        return True

    @property
    @require_determinism
    def language(self):
        from collections import deque
        try:
            alph = list(sorted(self.alphabet))
        except:
            alph = self.alphabet
        q = deque()
        with self.parent as machine:
            accepting = machine().reachable_states & machine().accepting_states
            q.append(())
            while q:
                thisword = q.popleft()
                machine().reset()
                machine(thisword)
                if machine:
                    yield thisword
                if machine().state.reachable & accepting:
                    for a in alph:
                        q.append(thisword + (a,))

    def polyfill(self, target=None):
        for state in self.states:
            for transition in self.alphabet:
                if not transition in state:
                    if not target:
                        state[(transition,)] = state
                    else:
                        state[(transition,)] = target

class FSM_State(object):
    """State of a finite state machine"""
    def __init__(self, parent, name):
        self.__parent = parent
        self.__following = {}
        self.__name = name
        self.__accepting = False

    def __call__(self, transition):
        return self.__following[transition]

    @property
    def accepting(self):
        return self.__accepting

    @accepting.setter
    def accepting(self, value):
        if value is True or value is False:
            self.__accepting = value
        else:
            raise TypeError("Accepting must be True or False")

    @property
    def parent(self):
        return self.__parent

    @property
    def name(self):
        return self.__name

    @property
    def transitions(self):
        return frozenset(self.__following.keys())

    @property
    def following(self):
        return frozenset(self.__following.values())

    def __reachable_shortest_paths(self):
        reachable = frozenset()
        reachable_states = lambda : frozenset(s for _,s in reachable)
        queue = {((), self)}
        done = set()

        while queue:
            this_prefix, this = queue.pop()

            if this in done:
                continue
            done.add(this)

            next_pairs = frozenset((this_prefix + (t,), this[t]) for t in this.transitions if not this[t] in reachable_states())
            reachable = reachable | next_pairs
            queue = queue | next_pairs
        return reachable

    def path_to(self, other):
        return next((f for f, s in self.__reachable_shortest_paths() if s is other), None)

    @property
    def reachable(self):
        return frozenset(s for _,s in self.__reachable_shortest_paths())

    def delete(self, f_state):
        to_delete = frozenset(key for key, value in self.__following.items() if value is f_state)
        for key in to_delete:
            del self[key]

    def __contains__(self, item):
        return item in self.__following

    def __str__(self):
        return '<state.%s>' % self.name

    def __setitem__(self, key, value):
        if not isinstance(value, FSM_State):
            raise TypeError("Transition target must be a state")
        elif not value.parent is self.parent:
            raise ValueError("States are not in the same machine")
        try:
            for v in key:
                self.__following[v] = value
        except TypeError:
            self.__following[key] = value

    def __getitem__(self, key):
        return self.__following[key]

    def __delitem__(self, key):
        del self.__following[key]

    def __gt__(self, other):
        # TODO: Raise value error if states from different machines
        return other in self.following

    def __lt__(self, other):
        # TODO: Raise value error if states from different machines
        return (other > self)

    def __rshift__(self, other):
        # TODO: Raise value error if states from different machines
        return other in self.reachable


def emmit_before(machine, transition):
    def __emmit(func):
        from functools import wraps
        @wraps(func)
        def wrapper(*args, **kwargs):
            machine(transition)
            return func(*args, **kwargs)
        return wrapper
    return __emmit
emmit = emmit_before

def emmit_after(machine, transition):
    def __emmit(func):
        from functools import wraps
        @wraps(func)
        def wrapper(*args, **kwargs):
            tmp = func(*args, **kwargs)
            machine(transition)
            return tmp
        return wrapper
    return __emmit
