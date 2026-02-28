"""
AWS Lambda handler for weather data ingestion.
This is the entry point that Lambda calls.
"""
import json
import logging
from datetime import datetime
from ingestion import main as run_ingestion

# Lambda uses CloudWatch Logs, so we set up logging to output there
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """
    AWS Lambda handler function.

    Args:
        event: Event data from trigger (EventBridge, manual invoke, etc.)
        context: Lambda runtime information

    Returns:
        dict: Status code and execution summary
    """
    logger.info("=" * 50)
    logger.info("Lambda function invoked")
    logger.info(f"Request ID: {context.aws_request_id}")
    logger.info(f"Event: {json.dumps(event)}")
    logger.info("=" * 50)

    try:
        #Run the ingestion pipeline
        result = run_ingestion()

        logger.info("Lambda execution completed successfully")

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Weather ingestion pipeline is successful',
                'timestamp': datetime.now().isoformat(),
                'result': result
            })
        }
    
    except Exception as e:
        logger.error(f"Lambda execution failed: {str(e)}", exc_info=True)

        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Weather ingestion pipeline is failed',
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'request_id': context.aws_request_id
            })
        }