r"""ssfsm is a finite-state-machine implementation with the most simple syntax
I could come up with."""

VERSION = "0.6.0"

from . import dfa
DFA_Machine = dfa.DFA_Machine
DFA_State = dfa.DFA_State
emmit = dfa.emmit
emmit_after = dfa.emmit_after
emmit_before = dfa.emmit_before

def Machine(*nargs, **kwargs):
    """Returns a new :py:class:`DFA_Machine`"""
    return DFA_Machine(*nargs, **kwargs)

def DFA(*nargs, **kwargs):
    return DFA_Machine(*nargs, **kwargs)
