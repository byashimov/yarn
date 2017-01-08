yarn
====

.. image:: https://travis-ci.org/byashimov/yarn.svg?branch=develop
    :alt: Build Status
    :target: https://travis-ci.org/byashimov/yarn

.. image:: https://codecov.io/gh/byashimov/yarn/branch/develop/graph/badge.svg
    :alt: Codecov
    :target: https://codecov.io/gh/byashimov/yarn


Makes generator cache it's result and act like a regular sequence.

.. code-block:: python

    from yarn import yarn

    def gen(x):
        for y in range(x):
            print('Gets from generator "{}"'.format(y))
            yield y

    foo = yarn(gen(10))
    foo[3]  # Iterates the generator
    Gets from generator "0"
    Gets from generator "1"
    Gets from generator "2"
    Gets from generator "3"
    3

    foo[3]  # This time it has a cache
    3

    foo.cache
    [0, 1, 2, 3]

    foo[4]
    Gets from generator "4"
    4


Can be used to get multiple results:

.. code-block:: python

    foo = yarn(gen(10))
    bar = yarn(x for x in foo if x > 5)
    baz = yarn(x for x in bar if x > 7)

    # Affects all yarns in the chain
    baz[0]
    Gets from generator "0"
    Gets from generator "1"
    ...
    Gets from generator "8"
    9

    baz.cache
    [8]

    bar.cache
    [6, 7, 8]

    foo.cache
    [0, 1, 2, 3, 4, 5, 6, 7, 8]

The last element (9) is still not fetched.

Gotchas
-------

Just like with ``itertools.tee`` never use the original generator first
if it's passed to another ``yarn``. Once it's empty it comes useless:

.. code-block:: python

    foo = yarn(gen(10))
    bar = yarn(x for x in foo if x > 5)

    # Runs iterator, which has no cache yet, skips it, iterates foo
    bar[0] == 3

    # At this point foo has no enough cache for the last index.
    # Original generator is used instead
    foo[-1] == 9

    # bar's iterator continues iterating foo (cache was skipped earlier).
    # foo is empty now
    bar[-1] == 3  # not 9


Use tee_ instead:

.. code-block:: python

    from itertools import tee

    fgen, bgen = tee(gen(10))
    foo = yarn(fgen)
    bar = yarn(x for x in bgen if x > 5)

    bar[0] == 3
    foo[-1] == 9
    bar[-1] == 9


But if ``foo`` had been cached first, everything is ok,
``bar`` will get ``foo``'s cache.


Features
--------

- caches it's result, which can be iterated over and over again
- supports both positive and negative indexing (in a lazy way)
- supports slices (lazy). Unlike ``itertools.tee`` supports negative slicing
- supports ``len`` (fetches everything)
- supports ``bool`` which is lazy (only first element is fetched)


Installation
------------

.. code-block:: console

    pip install -e git://github.com/byashimov/yarn.git#egg=yarn


Misc
----

- ``yarn`` is python >= 3.5 only.
- It's distributed under wtfpl_ license.
- Generators are tricky, don't fuck with them :(


.. _tee: https://docs.python.org/3/library/itertools.html#itertools.tee
.. _wtfpl: http://www.wtfpl.net/txt/copying/
