import unittest
from app import app,messages
 
class TestUM(unittest.TestCase):

    
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
 
    
    def test_get(self):
        #self.app = app
        rv = self.app.get('/')
        

       #  assert b'No entries here so far' in rv.data
        self.assertEqual(
                messages.HELLO,
                 rv.data.decode('utf-8'))
    
    def test_post(self):
        #self.app = app
        item = 'HELLO'
        rv = self.app.post('/hello',
                            data=item,
                            content_type='application/json')
        

       #  assert b'No entries here so far' in rv.data
        self.assertEqual(
                messages.HELLO,
                 rv.data.decode('utf-8'))

if __name__ == '__main__':
    unittest.main()