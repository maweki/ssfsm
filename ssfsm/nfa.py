try:
    from collections.abc import Set
except ImportError: #python 2.7 compat
    from collections import Set
from functools import reduce

class NFA_Machine(object):

    __states = None
    __alphabet = None
    __current_state = None
    __initial_state = None

    def __init__(self, initial_state=None):
        self.__states = {}
        self.__alphabet = frozenset()
        if initial_state:
            self.__current_state = frozenset((self[initial_state],))
            self.__initial_state = self[initial_state]
        else:
            self.__current_state = frozenset()
            self.__initial_state = None

    def __create_state(self, name):
        if name in self:
            raise ValueError("State allready created")
        new_state = NFA_State(self, name)
        self.__states[name] = new_state
        return new_state

    def __get_state(self, name):
        if name in self:
            return self.__states[name]
        return self.__create_state(name)

    def __getitem__(self, state):
        return self.__get_state(state)

    def __getattr__(self, state):
        return self.__get_state(state)

    def __setitem__(self, state, value):
        if value in (True, False):
            #accepting
            self[state].accepting = value
        else:
            # raise something
            pass

    def __setattr__(self, state, value):
        if state.startswith('_'):
            return object.__setattr__(self, state, value)
        self[state] = value

    def __delattr__(self, state):
        del self[state]

    def __delitem__(self, state):
        del self.__states[state]
        for s in self.__states.values():
            for transition in s:
                if s[transition] is state:
                    del s[transition]

    def __contains__(self, state):
        return state in self.__states

    def __call__(self, *args):
        return NFA_Machine_Controller(self)

    def __bool__(self):
        return any(s.accepting for s in self.__current_state)

    def __nonzero__(self):
        return any(s.accepting for s in self.__current_state)

    def __call__(self, transition=None):
        if transition is None:
            return NFA_Machine_Controller(self)

        # do transition
        result = frozenset()
        for state in self.__current_state:
            result = result | frozenset(state[transition])
        self.__current_state = result
        return result

    def __len__(self):
        return len(self.__states)

    def __deepcopy(self):
        copy = NFA_Machine()
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

    def __toDFA(self):
        extract_names = lambda states: frozenset(s.name for s in states)
        from ssfsm.dfa import DFA_Machine
        from operator import or_
        dfa = DFA_Machine(frozenset([self.__initial_state.name]))
        alphabet = self().alphabet
        states = frozenset([frozenset([self.__initial_state])])
        done = frozenset()
        while states - done:
            current_states = next(iter(states - done))
            dfa[extract_names(current_states)] = any(c.accepting for c in current_states)
            for l in alphabet:
                following_states = reduce(or_, (c[l] for c in current_states), frozenset())
                dfa[extract_names(current_states)][l] = dfa[extract_names(following_states)]
                states = states | frozenset([frozenset(following_states)])
            done = done | frozenset([current_states])
        return dfa

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
                target_nodes = from_node[transition]
                for t in target_nodes:
                    collected_transitions[t].add(str(transition))

            for to_node in collected_transitions:
                sep = '' if all(len(str(t)) == 1 for t in collected_transitions[to_node]) else ', '
                statements += [ '%d -> %d [ label="%s" ]' % ( nodes[from_node], nodes[to_node], sep.join(sorted(collected_transitions[to_node])) ) ]

            if from_node is self.__initial_state:
                statements += [ '0 -> %d' % nodes[from_node] ]

        graph = 'digraph ID { stmt_list }'.replace('ID', str(id(self))).replace('stmt_list', ';\n'.join(statements))
        return graph


class NFA_Machine_Controller(object):

    def __init__(self, parent):
        self.__parent = parent

    @property
    def state(self):
        return self.parent._NFA_Machine__current_state

    @state.setter
    def state(self, states):
        if isinstance(states, Set) and all(s.parent is self.parent for s in states):
            self.parent._NFA_Machine__current_state = frozenset(states)

    @property
    def alphabet(self):
        s = self.parent._NFA_Machine__alphabet
        for state in self.states:
            s = s | state.transitions
        return s

    @property
    def states(self):
        return frozenset(self.parent._NFA_Machine__states.values())

    @property
    def parent(self):
        return self.__parent

    @property
    def initial_state(self):
        return self.parent._NFA_Machine__initial_state

    def reset(self, target=None):
        self.state = frozenset((self.initial_state,))

    @property
    def dot(self):
        return self.parent._NFA_Machine__toDot()

    def dfa(self):
        return self.parent._NFA_Machine__toDFA()

class NFA_State(object):

    def __init__(self, parent, name):
        self.__parent = parent
        self.__following = {}
        self.__name = name
        self.__accepting = False

    @property
    def accepting(self):
        return self.__accepting

    @accepting.setter
    def accepting(self, value):
        if value is True or value is False:
            self.__accepting = value
        else:
            raise TypeError("Accepting must be True or False")

    def __call__(self, transition):
        return self.__following[transition]

    def __iter__(self):
        return iter(self.__following)

    @property
    def transitions(self):
        return frozenset(self.__following.keys())

    @property
    def following(self):
        from operator import or_
        return reduce(or_, self.__following.values())

    @property
    def parent(self):
        return self.__parent

    @property
    def name(self):
        return self.__name

    def __getitem__(self, key):
        if not key in self.__following:
            self.__following[key] = NFA_State_Set()
        return self.__following[key]

    def __delitem__(self, key):
        del self.__following[key]

    def __setitem__(self, transition, target):
        if isinstance(target, self.__class__) and target.parent is self.parent:
            self.__following[transition] = NFA_State_Set((target,))
        else:
            #raise something
            pass

    def __str__(self):
        return '<state.%s>' % self.name

class NFA_State_Set(Set):
    def __init__(self, *args, **kwargs):
        if args:
            self.__set = set(args[0])
        elif kwargs:
            self.__set = set(kwargs)
        else:
            self.__set = set()

    def __contains__(self, key):
        return key in self.__set

    def __iadd__(self, key):
        self.__set.add(key)

    def __len__(self):
        return len(self.__set)

    def __iter__(self):
        return iter(self.__set)

    def __str__(self):
        return str(self.__set)

    def __repr__(self):
        return repr(self.__set)
