#!/usr/bin/python3

import http.client as httplib
import unittest


class TestRequestResponse(unittest.TestCase):
    def setUp(self):
        self.conn = httplib.HTTPConnection('127.0.0.1', 80, timeout=1)

    def tearDown(self):
        self.conn.close()

    def test_ip_ok(self):
        """Normal IP - OK"""
        self.conn.request("GET", "/ip2w/195.69.81.52")
        r = self.conn.getresponse()
        self.assertEqual(200, int(r.status))
        r.msg

    def test_incorrect_or_no_ip(self):
        """Incorrect or no IP - 400"""
        self.conn.request("GET", "/ip2w/111.1111")
        r = self.conn.getresponse()
        self.assertEqual(400, int(r.status))
        self.conn.request("GET", "/ip2w/")
        r = self.conn.getresponse()
        self.assertEqual(400, int(r.status))

    def test_nolocation_ip(self):
        """Local IP - 500"""
        self.conn.request("GET", "/ip2w/127.0.0.1")  # IP w/o location
        r = self.conn.getresponse()
        self.assertEqual(500, int(r.status))


loader = unittest.TestLoader()
suite = unittest.TestSuite()
loaded_tests = loader.loadTestsFromTestCase(TestRequestResponse)
suite.addTest(loaded_tests)


class NewResult(unittest.TextTestResult):
    def getDescription(self, test):
        doc_first_line = test.shortDescription()
        return doc_first_line or ""


class NewRunner(unittest.TextTestRunner):
    resultclass = NewResult


runner = NewRunner(verbosity=2)
runner.run(suite)
