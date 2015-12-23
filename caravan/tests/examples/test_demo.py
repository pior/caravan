import unittest

from caravan.examples.demo import Demo
from caravan.testing import valid_workflow_registration


class Test(unittest.TestCase):

    def test_registration(self):
        valid_workflow_registration(Demo)
