import boto3
import json
import pandas as pd
from datetime import datetime, timedelta

s3_client = boto3.client('s3')

def analyze_weather_data(bucket_name, days_back=7):
    """
    Analyzes weather data from the last N days
    """
    # List all processed files
    response = s3_client.list_objects_v2(
        Bucket=bucket_name,
        Prefix='processed/'
    )
    
    all_data = []
    
    for obj in response.get('Contents', []):
        # Read file
        file_obj = s3_client.get_object(Bucket=bucket_name, Key=obj['Key'])
        data = json.loads(file_obj['Body'].read().decode('utf-8'))
        
        # Extract records
        for record in data.get('records', []):
            all_data.append(record)
    
    # Convert to DataFrame
    df = pd.DataFrame(all_data)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Analysis
    print("\n=== WEATHER DATA ANALYSIS ===")
    print(f"\nTotal records: {len(df)}")
    print(f"\nDate range: {df['timestamp'].min()} to {df['timestamp'].max()}")
    print(f"\nCities tracked: {df['city'].unique().tolist()}")
    
    print("\n=== TEMPERATURE STATISTICS (°C) ===")
    print(df.groupby('city')['temperature_celsius'].agg(['mean', 'min', 'max']).round(2))
    
    print("\n=== HUMIDITY STATISTICS (%) ===")
    print(df.groupby('city')['humidity_percent'].agg(['mean', 'min', 'max']).round(2))
    
    return df

# Usage
if __name__ == "__main__":
    bucket = "weather-processed-data-[your-name]"  # Update this
    df = analyze_weather_data(bucket)
    
    # Save locally
    df.to_csv('weather_analysis.csv', index=False)
    print("\nData saved to weather_analysis.csv")
