import unittest
import ip2w


class TestRequestResponseLocal(unittest.TestCase):
    def setUp(self):
        pass
        self.CONFIG: str = 'ip2w_dev.ini'
        self.env: dict = dict()
        self.env['PATH_INFO'] = '/ip2w/195.69.81.52'
        self.env['REMOTE_ADDR'] = '127.0.0.1'


    def tearDown(self):
        pass

    def test_response(self):
        CONFIG = self.CONFIG
        print(ip2w.application(self.env, print))
        # response = urllib.request.urlopen("http://localhost:8000")
        # self.assertEqual(response.getcode(), 200)
        # content = response.read().decode("utf-8")
        # self.assertEqual(content, "Hello, world!")

if __name__ == "__main__":
    unittest.main()