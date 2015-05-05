from distutils.core import setup

setup(
    name="ssfsm",
    packages = ['ssfsm'],
    version="0.5.0",
    author="Mario Wenzel",
    author_email="maweki@gmail.com",
    url="https://github.com/maweki/ssfsm",
    description="ssfsm is a constructive library implementing deterministic finite state machines. The fun thing is, that it has a stupidly simple API.",
    license="GPL 2.0",
    classifiers=[
"Programming Language :: Python :: 2.7",
"Programming Language :: Python :: 3",
"Programming Language :: Python :: 3.0",
"Programming Language :: Python :: 3.3",
"Programming Language :: Python :: 3.4",
"Operating System :: OS Independent",
"Development Status :: 5 - Production/Stable",
"Intended Audience :: Developers",
"Intended Audience :: Science/Research",
"Intended Audience :: Education",
"License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
"Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)",
"Topic :: Software Development :: Libraries :: Python Modules"
],
    long_description=
"""
ssfsm is a constructive library implementing deterministic finite state machines. The fun thing is, that it has a stupidly simple API.
Example::
    # A FSM that accepts b*a(ab)*
    import ssfsm
    A = ssfsm.Machine()
    A.One['a'] = A.Two
    A.One['b'] = A.One
    A.Two['ab'] = A.Two # a and b transition
    A.Two = True # Set state Two to accepting
    A().reset(A.One)

And transitions are done this way::

    A('a') # a-Transition
    A('ab') # a-Transition followed by b-Transition
    bool(A) # is A in an accepting state

Some helpers to make construction even easier so the first example can be written as::

    import ssfsm
    A = ssfsm.Machine('One')
    A().alphabet = 'ab'
    A.One['b'] = A.One
    A().polyfill(A.Two)
    A.Two = True
"""
)
