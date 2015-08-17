r"""ssfsm is a finite-state-machine implementation with the most simple syntax
I could come up with."""

VERSION = "0.6.0"

from . import dfa
FSM_Machine = dfa.FSM_Machine
FSM_State = dfa.FSM_State
emmit = dfa.emmit
emmit_after = dfa.emmit_after
emmit_before = dfa.emmit_before

def Machine(*nargs, **kwargs):
    """Returns a new :py:class:`FSM_Machine`"""
    return FSM_Machine(*nargs, **kwargs)
