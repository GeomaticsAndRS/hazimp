# -*- coding: utf-8 -*-

# Copyright (C) 2012-2013  Geoscience Australia

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# pylint: disable=C0103
# Since function names are based on what they are testing,
# and if they are testing classes the function names will have capitals
# C0103: 16:TestCalcs.test_AddTest: Invalid name "test_AddTest"
# (should match [a-z_][a-z0-9_]{2,50}$)
# pylint: disable=R0904
# Disable too many public methods for test cases
# pylint: disable=E1123
# pylint says;  Passing unexpected keyword argument 'delete' in function call
# I need to pass it though.
# pylint: disable=R0801

"""
Test the misc module.
"""

import unittest
import tempfile
import os

import numpy
from scipy import allclose

from hazimp.misc import (csv2dict, get_required_args, sorted_dict_values,
                              squash_narray, weighted_values)


class TestMisc(unittest.TestCase):

    """
    Test the calcs module
    """

    def test_csv2dict(self):
        # Write a file to test
        f = tempfile.NamedTemporaryFile(suffix='.txt',
                                        prefix='test_misc',
                                        delete=False,
                                        mode='w+t')
        f.write('X, Y, Z, A\n')
        f.write('1., 2., 3., yeah\n')
        f.write('4., 5., 6.,me \n')
        f.close()

        file_dict = csv2dict(f.name)

        actual = {'X': numpy.array([1.0, 4.0]),
                  'Y': numpy.array([2.0, 5.0]),
                  'Z': numpy.array([3.0, 6.0]),
                  'A': numpy.array(['yeah', 'me'])}
        for key in actual:
            if key == "A":
                self.assertTrue(list(file_dict[key]),
                                list(actual[key]))
            else:
                self.assertTrue(allclose(file_dict[key],
                                         actual[key]))
        os.remove(f.name)

    def test_get_required_args(self):
        def yeah(mandatory, why=0, me=1):
            """
            :param mandatory:
            :param why:
            :param me:
            :return:
            """
            return mandatory + why + me

        args, defaults = get_required_args(yeah)
        self.assertTrue(args == ['mandatory'])
        self.assertTrue(defaults == ['why', 'me'])

    def test_get_required_args2(self):
        def yeah(mandatory):
            """
            :param mandatory:
            :return:
            """
            return mandatory

        args, defaults = get_required_args(yeah)
        self.assertTrue(args == ['mandatory'])
        self.assertTrue(defaults == [])

    def test_get_required_args3(self):
        def yeah(mandatory=0):
            """
            :param mandatory:
            :return:
            """
            return mandatory

        args, defaults = get_required_args(yeah)
        self.assertTrue(defaults == ['mandatory'])
        self.assertTrue(args == [])

    def test_squash_narray(self):
        narray = numpy.array([[[50, 150], [45, 135]],
                              [[52, 152], [47, 137]],
                              [[54, 154], [49, 139]]])
        narray_copy = numpy.empty_like(narray)
        narray_copy[:] = narray
        squashed = squash_narray(narray)

        # Make sure
        self.assertTrue(allclose(narray, narray_copy))
        self.assertTrue(allclose(squashed, numpy.array([95., 97., 99.])))

    def test_squash_narray2(self):
        narray = numpy.array([[['B', 'O'], ['A', 'T']],
                              [['A', 'T'], ['O', 'm']],
                              [['M', 'O'], ['w gras', 's']]])
        squashed = squash_narray(narray)
        self.assertListEqual(squashed.tolist(), ['B', 'A', 'M'])

    def test_weighted_values_close_to_1(self):
        values = numpy.array([1.0, 2.0, 3.0])
        probabilities = numpy.array([0.33, 0.33, 0.33])
        size = (5,)
        forced_random = numpy.array([0.32, 0.34, 0.65, 0.7, 0.99])
        result = weighted_values(values, probabilities, size,
                                 forced_random=forced_random)
        actual = numpy.array([1, 2, 2, 3, 3])
        msg = 'fail. ' + str(result) + '!=' + str(actual)
        self.assertTrue(allclose(result, actual), msg)

    def test_weighted_values_bad_sum(self):
        values = numpy.array([1.1, 2.2, 3.3])
        probabilities = numpy.array([1000.2, 0.5, 0.8])
        size = (5,)
        self.assertRaises(RuntimeError, weighted_values, values,
                          probabilities, size)

    def test_weighted_values_bad_array_size(self):
        values = numpy.array([1.1, 2.2, 3.3])
        probabilities = numpy.array([0.5, 0.3])
        size = (5,)
        self.assertRaises(AssertionError, weighted_values, values,
                          probabilities, size)

    def test_weighted_values_check_results(self):
        values = numpy.array([1.0, 2.0, 3.0])
        probabilities = numpy.array([0.2, 0.5, 0.3])
        size = (5,)
        forced_random = numpy.array([0.19, 0.21, 0.69, 0.71, 0.99])
        result = weighted_values(values, probabilities, size,
                                 forced_random=forced_random)
        actual = numpy.array([1, 2, 2, 3, 3])
        msg = 'fail. ' + str(result) + '!=' + str(actual)
        self.assertTrue(allclose(result, actual), msg)

    def test_weighted_values_2d_array(self):
        values = numpy.array([1.0, 2.0, 3.0])
        probabilities = numpy.array([0.2, 0.5, 0.3])
        size = (2, 3)
        forced_random = numpy.array([[0.19, 0.21, 0.69], [0.71, 0.99, 0.5]])
        self.assertRaises(AssertionError, weighted_values, values,
                          probabilities, size, forced_random=forced_random)

    def test_sorted_dict_values(self):
        adict = {'socks': 3, 'feet': 2, 'boots': 1}
        r_keys, r_values = sorted_dict_values(adict)
        self.assertEqual(r_keys, ['boots', 'feet', 'socks'])
        self.assertEqual(r_values, [1, 2, 3])

#  -------------------------------------------------------------
if __name__ == "__main__":
    Suite = unittest.makeSuite(TestMisc, 'test')
    Runner = unittest.TextTestRunner()
    Runner.run(Suite)
