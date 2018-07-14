import unittest
from app.Algorithm import Algorithm


class AlgorithmTestCase(unittest.TestCase):
    def setUp(self):
        self.algo = Algorithm()

    def tearDown(self):
        self.algo = None

    def test_Add(self):
        self.assertEqual(self.algo.add(1, 2), 3)

    def test_Minus(self):
        self.assertEqual(self.algo.minus(3, 1), 2)


# def suite():
#     suite = unittest.TestSuite()
#     suite.addTest(AlgorithmTestCase("test_Add"))
#     suite.addTest(AlgorithmTestCase("test_Minus"))
#     return suite


if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(AlgorithmTestCase("test_Add"))
    suite.addTest(AlgorithmTestCase("test_Minus"))
    with open('UnittestTextReport.txt', 'a') as f:
        runner = unittest.TextTestRunner(stream=f, verbosity=2)
        result = runner.run(suite)
        print 'result = ' + result

