import json
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from src.lambda_handler import lambda_handler


@pytest.fixture
def mock_context():
    """Creates a mock Lambda context object."""
    context = MagicMock()
    context.aws_request_id = "test-request-id-123"
    return context


@pytest.fixture
def mock_event():
    """Creates a sample Lambda event."""
    return {"source": "aws.events", "detail-type": "Scheduled Event"}


def test_lambda_handler_success(mock_event, mock_context):
    """Test that handler returns 200 when ingestion succeeds."""
    # FIX: The patch path must match the import 'src.lambda_handler'
    with patch("src.lambda_handler.run_ingestion") as mock_run:
        mock_run.return_value = {"records_processed": 100}

        response = lambda_handler(mock_event, mock_context)

        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert body["result"]["records_processed"] == 100
        mock_run.assert_called_once()


def test_lambda_handler_failure(mock_event, mock_context):
    """Test that handler returns 500 when ingestion raises an exception."""
    # FIX: The patch path must match the import 'src.lambda_handler'
    with patch("src.lambda_handler.run_ingestion") as mock_run:
        mock_run.side_effect = Exception("Database connection timeout")

        response = lambda_handler(mock_event, mock_context)

        assert response["statusCode"] == 500
        body = json.loads(response["body"])
        assert "Database connection timeout" in body["error"]
        mock_run.assert_called_once()
