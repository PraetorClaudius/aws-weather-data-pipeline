# Weather Data Pipeline on AWS

## Project Overview
Automated data engineering pipeline that collects, processes, and stores weather data for major Mexican cities using AWS serverless architecture.

## Architecture
┌─────────────────────────────────────────────────────────────────────────┐
│                         WEATHER DATA PIPELINE                            │
└─────────────────────────────────────────────────────────────────────────┘

    ┌──────────────────┐
    │  OpenWeatherMap  │
    │    API (2.5)     │
    │  (External API)  │
    └────────┬─────────┘
             │ HTTP Request (every 6h)
             │
             ▼
    ┌──────────────────┐         ┌─────────────────────┐
    │   EventBridge    │────────▶│  Lambda Function    │
    │  Schedule Rule   │ Trigger │  data-collector     │
    │  (every 6 hours) │         │  • Fetch weather    │
    └──────────────────┘         │  • 5 Mexican cities │
                                 └──────────┬──────────┘
                                            │ Write JSON
                                            ▼
                                 ┌─────────────────────┐
                                 │    Amazon S3        │
                                 │  weather-raw-data   │
                                 │  • Raw JSON files   │
                                 │  • Date partitioned │
                                 │  raw/YYYY/MM/DD/    │
                                 └──────────┬──────────┘
                                            │ Read
                                            ▼
                                 ┌─────────────────────┐
                                 │  Lambda Function    │
                                 │  data-processor     │
                                 │  • Clean data       │
                                 │  • Calculate stats  │
                                 └──────────┬──────────┘
                                            │ Write
                                            ▼
                                 ┌─────────────────────┐
                                 │    Amazon S3        │
                                 │ weather-processed   │
                                 │  • Cleaned data     │
                                 │  • Aggregations     │
                                 │  processed/YYYY/    │
                                 └──────────┬──────────┘
                                            │ Download (optional)
                                            ▼
                                 ┌─────────────────────┐
                                 │  Analysis Script    │
                                 │  (Local - Python)   │
                                 │  • Pandas analysis  │
                                 │  • CSV export       │
                                 └─────────────────────┘

## Technologies Used
- **AWS Lambda**: Serverless compute for data collection and processing
- **AWS S3**: Data lake storage (raw and processed data)
- **AWS EventBridge**: Workflow automation and scheduling
- **Python 3.11**: Data processing logic
- **OpenWeatherMap API**: Data source

## Features
- Automated data collection every 6 hours
- Raw data storage with date partitioning
- Data cleaning and transformation
- Statistical aggregations
- Cost-optimized (runs entirely on AWS Free Tier)

## Data Pipeline Flow
1. EventBridge triggers Lambda every 6 hours
2. Lambda collects weather data from API for 5 Mexican cities
3. Raw JSON data stored in S3 with YYYY/MM/DD partitioning
4. Processor Lambda transforms and cleans data
5. Processed data stored in separate S3 bucket

## Setup Instructions
[Include your setup steps]

## Sample Output
[Include a sample JSON output]

## Future Improvements
- Add data visualization dashboard
- Implement data quality checks
- Add more cities
- Create historical trend analysis
- Set up SNS notifications for extreme weather

## Author
Eduardo Arriaga Alejandre
[Your LinkedIn]
[Your GitHub]