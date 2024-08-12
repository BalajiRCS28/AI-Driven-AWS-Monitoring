import boto3
import json
import logging
import requests
from datetime import datetime, timedelta

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3_client = boto3.client('s3')
s3_bucket_name = 'gptresponses23'  # Replace with your S3 bucket name

def get_gpt_analysis(logs):
    api_key = ''  # Replace with your actual API key
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    max_prompt_length = 7692  # Adjusted to fit within token limits

    truncated_logs = logs[:max_prompt_length]
    prompt = (
        "Analyze the following CloudWatch logs and provide detailed insights on CPU performance over time for my EC2 instance. "
        "Look for trends, anomalies, spikes, or any noteworthy events that could explain performance changes. "
        "Include relevant statistics, patterns, or recommendations.\n"
        "Here are the logs:\n" + truncated_logs
    )

    data = {
        'model': 'gpt-3.5-turbo-instruct',
        'prompt': prompt,
        'max_tokens': 500
    }

    response = requests.post('https://api.openai.com/v1/completions', headers=headers, json=data)

    if response.status_code != 200:
        logger.error("Error from GPT API: %s", response.text)
        return None

    response_data = response.json()
    if 'choices' in response_data and len(response_data['choices']) > 0:
        return response_data['choices'][0]['text']
    else:
        logger.error("Invalid GPT response format: %s", response_data)
        return None

def upload_to_s3(file_name, content):
    s3_client.put_object(
        Bucket=s3_bucket_name,
        Key=file_name,
        Body=content
    )

def lambda_handler(event, context):
    try:
        client = boto3.client('cloudwatch')
        
        # Define the time range for the metrics
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=1)
        
        response = client.get_metric_statistics(
            Namespace='AWS/EC2',
            MetricName='CPUUtilization',
            Dimensions=[
                {
                    'Name': 'InstanceId',
                    'Value': ''  # Replace with your instance ID
                },
            ],
            StartTime=start_time,
            EndTime=end_time,
            Period=300,
            Statistics=['Average'],
            Unit='Percent'
        )
        
        def convert_datetime(obj):
            if isinstance(obj, datetime):
                return obj.strftime('%Y-%m-%dT%H:%M:%SZ')
            raise TypeError("Type not serializable")
        
        response_serialized = json.loads(json.dumps(response, default=convert_datetime))
        
        logger.info("CloudWatch get_metric_statistics response: %s", json.dumps(response_serialized))
        
        log_client = boto3.client('logs')
        log_group_name = '/aws/lambda/LambdaFunction2'  # Replace with your log group name
        streams_response = log_client.describe_log_streams(
            logGroupName=log_group_name,
            orderBy='LastEventTime',
            descending=True,
            limit=1
        )
        
        log_stream_name = streams_response['logStreams'][0]['logStreamName']
        
        logs_response = log_client.get_log_events(
            logGroupName=log_group_name,
            logStreamName=log_stream_name,
            limit=100,
            startFromHead=False
        )
        
        logs = "\n".join(event['message'] for event in logs_response['events'])
        
        gpt_analysis = get_gpt_analysis(logs)
        
        if gpt_analysis:
            upload_to_s3('logs.txt', logs)
            upload_to_s3('gpt_analysis.txt', gpt_analysis)
        
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'metrics': response_serialized,
                    'message': 'Logs and GPT analysis have been uploaded to S3.',
                    'analysis': gpt_analysis
                })
            }
        else:
            return {
                'statusCode': 500,
                'body': json.dumps({'error': 'Failed to get GPT analysis.'})
            }
        
    except Exception as e:
        logger.error("Error in lambda_handler: %s", e)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

