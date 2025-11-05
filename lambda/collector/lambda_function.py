import json
import boto3
import urllib3
from datetime import datetime
import os

# Initialize clients
s3_client = boto3.client('s3')
http = urllib3.PoolManager()

# List of cities to track
CITIES = [
    'Toluca,MX',
    'Mexico City,MX',
    'Guadalajara,MX',
    'Monterrey,MX',
    'Cancun,MX'
]

def lambda_handler(event, context):
    """
    Collects weather data from OpenWeatherMap API and stores in S3
    """
    api_key = os.environ['WEATHER_API_KEY']
    bucket_name = os.environ['RAW_BUCKET']
    
    results = []
    timestamp = datetime.utcnow()
    
    for city in CITIES:
        try:
            # Call weather API using urllib3
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
            response = http.request('GET', url, timeout=10.0)
            
            # Check if request was successful
            if response.status != 200:
                print(f"Error for {city}: HTTP {response.status}")
                continue
            
            # Parse JSON response
            weather_data = json.loads(response.data.decode('utf-8'))
            
            # Add metadata
            weather_data['collection_timestamp'] = timestamp.isoformat()
            weather_data['city_query'] = city
            
            results.append(weather_data)
            print(f"✓ Collected data for {city}")
            
        except Exception as e:
            print(f"Error collecting data for {city}: {str(e)}")
            continue
    
    # Save to S3
    if results:
        # Create S3 key with date partitioning
        date_path = timestamp.strftime('%Y/%m/%d')
        time_str = timestamp.strftime('%H%M%S')
        s3_key = f"raw/{date_path}/weather_{time_str}.json"
        
        # Upload to S3
        s3_client.put_object(
            Bucket=bucket_name,
            Key=s3_key,
            Body=json.dumps(results, indent=2),
            ContentType='application/json'
        )
        
        print(f"Successfully collected data for {len(results)} cities")
        print(f"Saved to: s3://{bucket_name}/{s3_key}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Data collection successful',
                'cities_count': len(results),
                's3_location': f"s3://{bucket_name}/{s3_key}"
            })
        }
    else:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'No data collected'})
        }