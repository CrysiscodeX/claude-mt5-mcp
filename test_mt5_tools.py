import unittest
from unittest.mock import patch, MagicMock

# Import the functions to be tested
from mt5_tools import get_account_info, initialize_mt5

class TestMT5Tools(unittest.TestCase):

    @patch('mt5_tools.mt5')
    def test_get_account_info_success(self, mock_mt5):
        """
        Test the get_account_info function for a successful call.
        """
        # Configure the mock to simulate successful initialization
        mock_mt5.initialize.return_value = True

        # Create a mock for the account info object
        mock_info = MagicMock()
        mock_info._asdict.return_value = {"login": 123, "balance": 1000}
        
        # Configure the mock mt5 library to return the mock info object
        mock_mt5.account_info.return_value = mock_info

        # Call the function
        result = get_account_info()

        # Assert the result is as expected
        self.assertEqual(result, {"login": 123, "balance": 1000})
        
        # Verify that initialize and account_info were called
        mock_mt5.initialize.assert_called_once()
        mock_mt5.account_info.assert_called_once()

    @patch('mt5_tools.mt5')
    def test_initialization_failure(self, mock_mt5):
        """
        Test that an exception is raised when MT5 initialization fails.
        """
        # Configure the mock to simulate failed initialization
        mock_mt5.initialize.return_value = False

        # Use assertRaises to check for the expected exception
        with self.assertRaises(Exception) as context:
            get_account_info()

        self.assertEqual(str(context.exception), "MT5 initialization failed")
        
        # Verify that initialize was called
        mock_mt5.initialize.assert_called_once()
        # Ensure account_info was not called because of the failure
        mock_mt5.account_info.assert_not_called()

if __name__ == '__main__':
    unittest.main()
