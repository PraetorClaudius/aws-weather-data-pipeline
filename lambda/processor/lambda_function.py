import json
import boto3
from datetime import datetime
import os

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    """
    Processes raw weather data and creates cleaned/aggregated version
    """
    raw_bucket = os.environ['RAW_BUCKET']
    processed_bucket = os.environ['PROCESSED_BUCKET']
    
    # Get the S3 object from the event trigger
    # For testing, we'll list latest file
    try:
        # List objects in raw bucket
        response = s3_client.list_objects_v2(
            Bucket=raw_bucket,
            Prefix='raw/'
        )
        
        if 'Contents' not in response or len(response['Contents']) == 0:
            return {
                'statusCode': 404,
                'body': json.dumps({'message': 'No raw data found'})
            }
        
        # Get the most recent file
        latest_file = sorted(response['Contents'], key=lambda x: x['LastModified'])[-1]
        s3_key = latest_file['Key']
        
        # Read raw data
        obj = s3_client.get_object(Bucket=raw_bucket, Key=s3_key)
        raw_data = json.loads(obj['Body'].read().decode('utf-8'))
        
        # Process data
        processed_records = []
        
        for record in raw_data:
            processed_record = {
                'city': record.get('name'),
                'country': record.get('sys', {}).get('country'),
                'timestamp': record.get('collection_timestamp'),
                'temperature_celsius': record.get('main', {}).get('temp'),
                'feels_like': record.get('main', {}).get('feels_like'),
                'humidity_percent': record.get('main', {}).get('humidity'),
                'pressure_hpa': record.get('main', {}).get('pressure'),
                'wind_speed_mps': record.get('wind', {}).get('speed'),
                'weather_description': record.get('weather', [{}])[0].get('description'),
                'cloudiness_percent': record.get('clouds', {}).get('all'),
                'latitude': record.get('coord', {}).get('lat'),
                'longitude': record.get('coord', {}).get('lon')
            }
            processed_records.append(processed_record)
        
        # Create summary statistics
        summary = {
            'processing_timestamp': datetime.utcnow().isoformat(),
            'total_cities': len(processed_records),
            'avg_temperature': sum(r['temperature_celsius'] for r in processed_records) / len(processed_records),
            'max_temperature': max(r['temperature_celsius'] for r in processed_records),
            'min_temperature': min(r['temperature_celsius'] for r in processed_records),
            'records': processed_records
        }
        
        # Save processed data
        timestamp = datetime.utcnow()
        date_path = timestamp.strftime('%Y/%m/%d')
        time_str = timestamp.strftime('%H%M%S')
        processed_key = f"processed/{date_path}/weather_processed_{time_str}.json"
        
        s3_client.put_object(
            Bucket=processed_bucket,
            Key=processed_key,
            Body=json.dumps(summary, indent=2),
            ContentType='application/json'
        )
        
        print(f"Processed {len(processed_records)} records")
        print(f"Saved to: s3://{processed_bucket}/{processed_key}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Processing successful',
                'records_processed': len(processed_records),
                's3_location': f"s3://{processed_bucket}/{processed_key}"
            })
        }
        
    except Exception as e:
        print(f"Error processing data: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }