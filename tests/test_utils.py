import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, Mock
from requests.exceptions import RequestException, Timeout
from src.utils import get_date_range, fetch_api_with_retry

"""Unit tests for utility functions in utils.py"""

class TestGetDateRange:
    """Test date range calculation"""

    def test_default_30_days(self):
        """Test default 30 days range"""
        start_date, end_date = get_date_range()
        start_date = datetime.fromisoformat(start_date).date()
        end_date = datetime.fromisoformat(end_date).date()
        assert (end_date - start_date).days == 30

    def test_custom_days(self):
        """Test custom days range"""
        start, end = get_date_range(days=7)
        start_date = datetime.fromisoformat(start).date()
        end_date = datetime.fromisoformat(end).date()
        assert (end_date - start_date).days == 7

    def test_end_date_is_yesterday(self):
        """Ensure end date is always yesterday"""
        _, end = get_date_range(days=10)
        expected_end = datetime.fromisoformat(end).date()
        yesterday = datetime.now().date() - timedelta(days=1)
        assert expected_end == yesterday
        

class TestFetchAPIWithRetry:
    """Test API fetching with retry logic"""

    @patch('src.utils.rq.get')
    def test_successful_fetch(self, mock_get):
        """Test that successful request on first try returns data"""

        mock_response = Mock()
        mock_response.json.return_value = {"data": "test"}
        mock_get.return_value = mock_response

        result = fetch_api_with_retry("http://fakeapi.com", params={})

        assert result == {"data": "test"}
        mock_get.assert_called_once()

    @patch('src.utils.rq.get')
    @patch('src.utils.time.sleep')
    def test_retry_logic_with_eventual_success(self, mock_sleep, mock_get):
        """Test that retry works and eventually returns data"""
        mock_response = Mock()
        mock_response.json.return_value = {"data": "test"}

        # First 2 attempts fail, 3rd succeeds
        mock_get.side_effect = [
            Timeout("Timeout error 1"),
            Timeout("Timeout error 2"),
            mock_response
        ]

        result = fetch_api_with_retry("http://fakeapi.com", params={}, max_retries=3, timeout=1)

        assert result == {"data": "test"}
        assert mock_get.call_count == 3
        assert mock_sleep.call_count == 2  # Sleep called between retries

    @patch('src.utils.rq.get')
    @patch('src.utils.time.sleep')
    def test_all_retries_fail(self, mock_sleep, mock_get):
        """Test that function returns None after all retries fail"""
        mock_get.side_effect = RequestException("Network error")

        result = fetch_api_with_retry("http://fakeapi.com", params={}, max_retries=3, timeout=1)

        assert result is None
        assert mock_get.call_count == 3

    @patch('src.utils.rq.get')
    @patch('src.utils.time.sleep')
    def test_exponential_backoff(self, mock_sleep, mock_get):
        """Test that sleep times increase exponentially between retries"""
        mock_get.side_effect = RequestException("Failed")

        fetch_api_with_retry("http://fakeapi.com", {}, max_retries=3)

        assert mock_sleep.call_count == 2
        mock_sleep.assert_any_call(2)  # First wait
        mock_sleep.assert_any_call(4)  # Second wait