import unittest
#from app import app
#app.testing = True
#from flask import request
#from app import messages

class TestCases(unittest.TestCase):

    def setUp(self):
        # print('In SetUp!')
        # app.testing = True
        # self.app = app.test_client()
        pass

 

    # def test_main(self):
    #      with app.test_client() as client:
    #         # send data as POST form to endpoint
    #         sent = {'hello'}
    #         result = client.post(
    #             '/hello',
    #             data=sent
    #         )
    #         # check result from server with expected data
    #         self.assertEqual(
    #             result.data,
    #             messages.HELLO
    #         ) 

    def test_myroutes(self):
       # rv = self.app.get('/')
       #  assert b'No entries here so far' in rv.data
        self.assertEqual(
                'Hello',
                 'Hello')
    
    def test_numbers_3_4(self):
        self.assertEqual(12, 12)
 
    def test_strings_a_3(self):
        self.assertEqual( 'aa', 'aaa')

    if __name__ == '__main__':
        unittest.main()