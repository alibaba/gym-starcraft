from __future__ import absolute_import

import unittest
import gym_starcraft.utils as utils


class UtilsTest(unittest.TestCase):
    def test_get_degree(self):
        self.assertEquals(utils.get_degree(10, -10, 10, -20), -90)
        self.assertEquals(utils.get_degree(10, -10, 10, -5), 90)
        self.assertEquals(utils.get_degree(10, -10, 5, -10), 180)
        self.assertEquals(utils.get_degree(10, -10, 15, -10), 0)
        self.assertEquals(utils.get_degree(10, -10, 20, -20), -45)

    def test_get_distance(self):
        self.assertEquals(utils.get_distance(10, -10, 10, -20), 10)
        self.assertEquals(utils.get_distance(10, -10, 10, -5), 5)
        self.assertEquals(utils.get_distance(10, -10, 5, -10), 5)
        self.assertEquals(utils.get_distance(10, -10, 15, -10), 5)

    def test_get_position(self):
        self.assertEquals(utils.get_position(90, 10, 10, -10), (10, 0))
        self.assertEquals(utils.get_position(0, 10, 10, -10), (20, -10))
        self.assertEquals(utils.get_position(180, 10, 10, -10), (0, -10))


if __name__ == '__main__':
    unittest.main()
