import sys
from collections import deque
from itertools import tee

import unittest2 as unittest

from . import yarn


class NegativeSlicingTestMixin:
    def test_negative_slice_start_only(self):
        sli = slice(-2, None, None)
        seq = yarn(self.seq)

        expected = [5, 6]
        self.assertCountEqual(self.seq_flat[sli], expected)
        self.assertCountEqual(seq[sli], expected)
        self.assertEqual(seq.cache, self.seq_flat)
        self.assertTrue(seq.is_cached)

    def test_negative_slice_stop_only(self):
        sli = slice(None, -2, None)
        seq = yarn(self.seq)

        expected = [0, 1, 2, 3, 4]
        self.assertCountEqual(self.seq_flat[sli], expected)
        self.assertCountEqual(seq[sli], expected)
        self.assertEqual(seq.cache, self.seq_flat)
        self.assertTrue(seq.is_cached)

    def test_negative_slice_start_with_negative_stop(self):
        sli = slice(2, -2, None)
        seq = yarn(self.seq)

        expected = [2, 3, 4]
        self.assertCountEqual(self.seq_flat[sli], expected)
        self.assertCountEqual(seq[sli], expected)
        self.assertEqual(seq.cache, self.seq_flat)
        self.assertTrue(seq.is_cached)

    def test_negative_slice_step_only(self):
        sli = slice(None, None, -2)
        seq = yarn(self.seq)

        expected = [6, 4, 2, 0]
        self.assertCountEqual(self.seq_flat[sli], expected)
        self.assertCountEqual(seq[sli], expected)
        self.assertEqual(seq.cache, self.seq_flat)
        self.assertTrue(seq.is_cached)

    def test_negative_slice_step_with_negative_stop(self):
        sli = slice(None, -2, -2)
        seq = yarn(self.seq)

        expected = [6]
        self.assertCountEqual(self.seq_flat[sli], expected)
        self.assertCountEqual(seq[sli], expected)
        self.assertEqual(seq.cache, self.seq_flat)
        self.assertTrue(seq.is_cached)

    def test_negative_slice_step_with_positive_stop(self):
        sli = slice(None, 2, -1)
        seq = yarn(self.seq)

        expected = [6, 5, 4, 3]
        self.assertCountEqual(self.seq_flat[sli], expected)
        self.assertCountEqual(seq[sli], expected)
        self.assertEqual(seq.cache, self.seq_flat)
        self.assertTrue(seq.is_cached)

    def test_negative_slice_step_with_positive_start(self):
        sli = slice(2, None, -1)
        seq = yarn(self.seq)

        expected = [2, 1, 0]
        self.assertCountEqual(self.seq_flat[sli], expected)
        self.assertCountEqual(seq[sli], expected)
        self.assertEqual(seq.cache, [0, 1, 2])
        self.assertFalse(seq.is_cached)

    def test_negative_slice_step_with_positive_start_and_stop(self):
        sli = slice(4, 2, -1)
        seq = yarn(self.seq)

        expected = [4, 3]
        self.assertCountEqual(self.seq_flat[sli], expected)
        self.assertCountEqual(seq[sli], expected)
        self.assertEqual(seq.cache, [0, 1, 2, 3, 4])
        self.assertFalse(seq.is_cached)


class PositiveSlicingTestMixin:
    def test_slice_start_only(self):
        sli = slice(3, None, None)
        seq = yarn(self.seq)

        expected = [3, 4, 5, 6]
        self.assertCountEqual(self.seq_flat[sli], expected)
        self.assertCountEqual(seq[sli], expected)
        self.assertEqual(seq.cache, self.seq_flat)
        self.assertTrue(seq.is_cached)

    def test_slice_stop_only(self):
        sli = slice(None, 3, None)
        seq = yarn(self.seq)

        expected = [0, 1, 2]
        self.assertCountEqual(self.seq_flat[sli], expected)
        self.assertCountEqual(seq[sli], expected)
        self.assertEqual(seq.cache, expected)
        self.assertFalse(seq.is_cached)

    def test_slice_step_only(self):
        sli = slice(None, None, 2)
        seq = yarn(self.seq)

        expected = [0, 2, 4, 6]
        self.assertCountEqual(self.seq_flat[sli], expected)
        self.assertCountEqual(seq[sli], expected)
        self.assertEqual(seq.cache, self.seq_flat)
        self.assertTrue(seq.is_cached)

    def test_slice_start_and_step_only(self):
        sli = slice(1, None, 2)
        seq = yarn(self.seq)

        expected = [1, 3, 5]
        self.assertCountEqual(self.seq_flat[sli], expected)
        self.assertCountEqual(seq[sli], expected)
        self.assertEqual(seq.cache, self.seq_flat)
        self.assertTrue(seq.is_cached)

    def test_slice_start_stop_step(self):
        sli = slice(1, 2, 2)
        seq = yarn(self.seq)

        expected = [1]
        self.assertCountEqual(self.seq_flat[sli], expected)
        self.assertCountEqual(seq[sli], expected)
        self.assertEqual(seq.cache, [0, 1])
        self.assertFalse(seq.is_cached)

    def test_slice_full_copy(self):
        sli = slice(None)
        seq = yarn(self.seq)

        self.assertIsInstance(seq[sli], yarn)

        # Doesn't run until iterated
        self.assertEqual(seq.cache, [])
        self.assertCountEqual(seq[sli], self.seq_flat)
        self.assertTrue(seq.is_cached)

    def test_slice_over_length(self):
        sli = slice(None, 999, None)
        seq = yarn(self.seq)

        self.assertIsInstance(seq[sli], yarn)
        self.assertCountEqual(seq, self.seq_flat)
        self.assertEqual(seq.cache, self.seq_flat)
        self.assertTrue(seq.is_cached)

    def test_slice_clone(self):
        foo = yarn(self.seq)
        bar = yarn(foo)
        baz = yarn(bar)

        # Iters last
        self.assertCountEqual(baz[:2], [0, 1])
        self.assertEqual(baz.cache, [0, 1])
        self.assertEqual(baz.cache, bar.cache)
        self.assertEqual(baz.cache, foo.cache)

        # Iters second
        self.assertCountEqual(bar[:4], [0, 1, 2, 3])
        self.assertEqual(bar.cache, [0, 1, 2, 3])
        self.assertEqual(bar.cache, foo.cache)

        # And the last still gets cache from the second
        self.assertCountEqual(baz[:5], [0, 1, 2, 3, 4])
        self.assertEqual(baz.cache, [0, 1, 2, 3, 4])
        self.assertEqual(baz.cache, bar.cache)
        self.assertEqual(baz.cache, foo.cache)

        # All of them return the full set
        self.assertCountEqual(foo[:7], self.seq_flat)
        self.assertCountEqual(bar[:7], self.seq_flat)
        self.assertCountEqual(baz[:7], self.seq_flat)


class IndexingTestMixin:
    def test_index_access(self):
        foo = yarn(self.seq)
        bar = yarn(foo)
        baz = yarn(bar)

        self.assertEqual(baz[2], 2)
        self.assertEqual(baz.cache, [0, 1, 2])
        self.assertEqual(baz.cache, bar.cache)
        self.assertEqual(baz.cache, foo.cache)

        self.assertEqual(bar[3], 3)
        self.assertEqual(bar.cache, [0, 1, 2, 3])
        self.assertEqual(bar.cache, foo.cache)
        self.assertEqual(baz.cache, [0, 1, 2])  # Still has old cache

        self.assertEqual(baz[5], 5)
        self.assertEqual(baz.cache, [0, 1, 2, 3, 4, 5])
        self.assertEqual(baz.cache, bar.cache)
        self.assertEqual(baz.cache, foo.cache)

        # Previous index access has cached all elements
        self.assertEqual(foo[1], 1)
        self.assertEqual(foo.cache, [0, 1, 2, 3, 4, 5])
        self.assertEqual(foo.cache, bar.cache)
        self.assertEqual(foo.cache, baz.cache)

    def test_index_negative_access(self):
        for seq in (self.seq_flat, yarn(self.seq)):
            with self.subTest(seq=seq):
                self.assertEqual(seq[-1], 6)

    def test_index_out_of_range(self):
        for seq in (self.seq_flat, yarn(self.seq)):
            with self.subTest(seq=seq):
                with self.assertRaises(IndexError):
                    seq[7]

    def test_index_clone(self):
        foo = yarn(self.seq)
        bar = yarn(foo)

        self.assertEqual(bar[0], 0)
        self.assertEqual(foo[-1], 6)
        self.assertEqual(bar[-1], 6)

    def test_index_chained_fails(self):
        foo = yarn(self.seq)
        bar = yarn(x for x in foo if x > 2)

        self.assertEqual(bar[0], 3)
        self.assertEqual(foo[-1], 6)

        # Fails, not 9
        self.assertEqual(bar[-1], 3)

    def test_index_chained_uses_tee(self):
        fgen, bgen = tee(self.seq)

        foo = yarn(fgen)
        bar = yarn(x for x in bgen if x > 2)

        self.assertEqual(bar[0], 3)
        self.assertEqual(foo[-1], 6)
        self.assertEqual(bar[-1], 6)


class SeqBehaviorTestMixin:
    def test_iter(self):
        foo = yarn(self.seq)
        bar = yarn(foo)
        baz = yarn(bar)

        self.assertEqual(next(iter(baz)), 0)
        self.assertEqual(baz.cache, [0])
        self.assertEqual(baz.cache, bar.cache)
        self.assertEqual(baz.cache, foo.cache)

    def test_iter_again(self):
        seq = yarn(self.seq)
        self.assertCountEqual(seq[:2], [0, 1])
        self.assertCountEqual(seq[:2], [0, 1])  # One more time, same cache

        self.assertEqual(seq.cache, [0, 1])
        self.assertEqual(next(iter(self.seq)), 2)  # Wasn't over iterated

    def test_next(self):
        foo = yarn(self.seq)
        bar = yarn(foo)
        baz = yarn(bar)

        self.assertEqual(next(iter(foo)), 0)
        self.assertEqual(next(iter(bar)), 0)
        self.assertEqual(next(iter(baz)), 0)
        self.assertEqual(next(iter(self.seq)), 1)

    def test_next_from_last(self):
        foo = yarn(self.seq)
        bar = yarn(foo)
        baz = yarn(bar)

        self.assertEqual(next(iter(baz)), 0)
        self.assertEqual(next(iter(bar)), 0)
        self.assertEqual(next(iter(foo)), 0)
        self.assertEqual(next(iter(self.seq)), 1)

    def test_len(self):
        foo = yarn(self.seq)
        bar = yarn(foo)
        baz = yarn(bar)

        self.assertEqual(len(baz), 7)
        self.assertEqual(foo.cache, self.seq_flat)

    def test_len_after_slice(self):
        seq = yarn(self.seq)

        self.assertCountEqual(seq[1::2], [1, 3, 5])
        self.assertEqual(len(seq), 7)

    def test_bool(self):
        foo = yarn(self.seq)
        bar = yarn(foo)
        baz = yarn(bar)

        self.assertTrue(baz)
        self.assertEqual(baz.cache, [0])
        self.assertEqual(baz.cache, bar.cache)
        self.assertEqual(baz.cache, foo.cache)
        self.assertEqual(next(iter(self.seq)), 1)


class ExpectedSetupTestMixin:
    seq = NotImplemented
    seq_flat = [0, 1, 2, 3, 4, 5, 6]

    def test_setup(self):
        self.assertEqual(len(self.seq_flat), 7)
        self.assertCountEqual(self.seq, self.seq_flat)


class LazySeqTestMixin(
        PositiveSlicingTestMixin,
        ExpectedSetupTestMixin,
        NegativeSlicingTestMixin,
        IndexingTestMixin,
        SeqBehaviorTestMixin):
    pass


class SugarGeneratorTest(LazySeqTestMixin, unittest.TestCase):
    def setUp(self):
        self.seq = (x for x in range(7))


class FunctionGeneratorTest(LazySeqTestMixin, unittest.TestCase):
    def setUp(self):
        def seq(x):
            yield from range(x)
        self.seq = seq(7)


class MapTest(LazySeqTestMixin, unittest.TestCase):
    def setUp(self):
        self.seq = map(int, range(7))


class FilterTest(LazySeqTestMixin, unittest.TestCase):
    def setUp(self):
        self.seq = filter(lambda x: True, range(7))


class InMemorySeqTestMixin(ExpectedSetupTestMixin):
    def test_is_cached(self):
        self.assertTrue(self.seq.is_cached)

    def test_iter(self):
        self.assertCountEqual(self.seq, self.seq_flat)

    def test_len(self):
        self.assertEqual(len(self.seq), len(self.seq_flat))

    def test_index_access(self):
        self.assertEqual(self.seq[0], self.seq_flat[0])
        self.assertEqual(self.seq[-1], self.seq_flat[-1])

    def test_slicing(self):
        self.assertCountEqual(self.seq[1:], self.seq_flat[1:])
        self.assertCountEqual(self.seq[2:3], self.seq_flat[2:3])
        self.assertCountEqual(self.seq[::1], self.seq_flat[::1])

    def test_bool(self):
        self.assertEqual(bool(self.seq), bool(self.seq_flat))

    def test_clone(self):
        child = self.seq[3:]

        self.assertIsInstance(child, yarn)
        self.assertEqual(child[0], 3)

        # Sliced in memory type returns new yarn with cache of the same type
        self.assertCountEqual(child.cache, [3, 4, 5, 6])


class ListTest(InMemorySeqTestMixin, unittest.TestCase):
    def setUp(self):
        self.seq = yarn(list(range(7)))


class TupleTest(InMemorySeqTestMixin, unittest.TestCase):
    def setUp(self):
        self.seq = yarn(tuple(range(7)))


@unittest.skipIf(sys.version_info < (3, 5), 'Doesn\'t support deque under 3.5')
class DequeTest(InMemorySeqTestMixin, unittest.TestCase):
    def setUp(self):
        self.seq = yarn(deque(range(7)))

    def test_slicing(self):
        # Deque doesn't support slicing
        with self.assertRaises(TypeError):
            self.seq[1:]

    def test_clone(self):
        pass


class RangeTest(InMemorySeqTestMixin, unittest.TestCase):
    def setUp(self):
        self.seq = yarn(range(7))


class GeneralStuffTest(unittest.TestCase):
    def test_not_iter(self):
        with self.assertRaises(TypeError):
            yarn(object())

    def test_repr(self):
        seq = yarn(x for x in range(7))
        seq[3]  # Creates cache
        self.assertEqual(repr(seq), '<yarn [0, 1, 2, 3]>')
