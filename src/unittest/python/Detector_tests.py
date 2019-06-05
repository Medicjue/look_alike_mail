# -*- coding: utf-8 -*-

import unittest
from Detector import Detector

class DetectorTestCase(unittest.TestCase):
    def setUp(self):
        self.detector = Detector()
    
    def test_check_substr(self):
        word1 = 'abc'
        word2 = 'abcd'
        is_substr, substr_index = self.detector.check_substr(word1, word2)
        print(is_substr, substr_index)
        self.assertEqual(is_substr, True)
        self.assertEqual(substr_index, 0)
        
    def test_decompose_email_address(self):
        mail_acct, mail_domain = self.detector.decompose_email_address('test@gmail.com')
        self.assertEqual(mail_acct, 'test')
        self.assertEqual(mail_domain, 'gmail.com')
        
        self.assertRaises(ValueError, self.detector.decompose_email_address, 'test.gmail.com')