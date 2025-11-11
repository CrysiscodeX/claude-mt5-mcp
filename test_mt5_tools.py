import unittest
from unittest.mock import patch, MagicMock
from mt5_tools import get_account_info

class TestMT5Tools(unittest.TestCase):

    @patch('mt5_tools.mt5')
    def test_get_account_info_success(self, mock_mt5):
        mock_mt5.initialize.return_value = True
        mock_info = MagicMock()
        mock_info._asdict.return_value = {"login": 123}
        mock_mt5.account_info.return_value = mock_info
        
        result = get_account_info()
        
        self.assertEqual(result, {"login": 123})

    @patch('mt5_tools.mt5')
    def test_get_account_info_failure(self, mock_mt5):
        mock_mt5.initialize.return_value = False
        
        result = get_account_info()
        
        self.assertTrue(result.get('error'))
        self.assertIn("MT5 initialization failed", result.get('message'))

if __name__ == '__main__':
    unittest.main()