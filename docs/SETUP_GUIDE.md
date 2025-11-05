STEP 0: Safety First (Do This FIRST!)
Set Up Billing Alarm

Log into AWS Console
Go to CloudWatch → Alarms → Billing
Create alarm:

Threshold: $5 USD
Email: your email
Confirm the subscription email you receive

Enable Free Tier Alerts

Go to Billing Dashboard
Click Billing Preferences
Enable "Receive Free Tier Usage Alerts"
Save preferences

✅ CHECKPOINT: You should receive a confirmation email. Don't proceed until this is done!


STEP 1: Project Setup & Planning
1.1 Get Your Free Weather API Key

Go to OpenWeatherMap
Sign up for free account
Get your API key (Free tier: 1000 calls/day)
Test the API in your browser:

   https://api.openweathermap.org/data/2.5/weather?q=Toluca,MX&appid=YOUR_API_KEY&units=metric
1.2 Define Your Data Pipeline
What data to collect:

Current weather for 5-10 Mexican cities (Toluca, CDMX, Guadalajara, Monterrey, Cancún, etc.)
Temperature, humidity, pressure, wind speed
Collect every 6 hours (4 times per day = ~120 API calls/day, well within free limit)

Pipeline flow:
Weather API → Lambda (collect) → S3 (raw data) → Lambda (process) → S3 (processed data)
                ↑
          EventBridge (trigger every 6h)


STEP 2: Set Up S3 Buckets
2.1 Create S3 Buckets

Go to S3 in AWS Console
Click Create bucket
Create TWO buckets:

Name: weather-raw-data-[your-name] (e.g., weather-raw-data-juan)
Region: Choose closest to you (us-east-1 is cheapest)
Keep all default settings
Click Create bucket

Repeat for second bucket:

Name: weather-processed-data-[your-name]


STEP 3: Build Data Collector Lambda
3.1 Write the Collector Code
Create lambda_function.py for the collector:

Code in collector folder

3.2 Create Lambda Function in AWS

Go to Lambda in AWS Console
Click Create function
Choose Author from scratch
Settings:

Function name: weather-data-collector
Runtime: Python 3.11
Architecture: x86_64
Click Create function

3.3 Upload Your Code

In the Lambda function page, scroll to Code source
Delete the default code
Copy and paste your lambda_function.py code
Click Deploy

3.4 Add Requests Library (Lambda Layer)
Since requests isn't included by default:

Scroll down to Layers
Click Add a layer
Choose AWS layers
Select AWSSDKPandas-Python311 (includes requests)
Click Add

3.5 Configure Environment Variables

Go to Configuration tab → Environment variables
Click Edit → Add environment variable
Add two variables:

Key: WEATHER_API_KEY, Value: [your OpenWeatherMap API key]
Key: RAW_BUCKET, Value: weather-raw-data-[your-name]

Click Save

3.6 Set Lambda Timeout & Permissions

Go to Configuration → General configuration
Click Edit
Set timeout to 30 seconds
Click Save
Go to Configuration → Permissions
Click on the role name (opens IAM)
Click Add permissions → Attach policies
Search and attach: AmazonS3FullAccess (for learning; in production use minimal permissions)
Click Add permissions

3.7 Test Your Lambda

Go back to Lambda function
Click Test tab
Create new test event:

Event name: TestCollect
Event JSON: {}


Click Save
Click Test


STEP 4: Build Data Processor Lambda
4.1 Write the Processor Code
Create second Lambda function code:

Code in processor folder

4.2 Create Processor Lambda

Go to Lambda → Create function
Function name: weather-data-processor
Runtime: Python 3.11
Click Create function
Paste the processor code
Click Deploy

4.3 Configure Processor Lambda

Add environment variables:

RAW_BUCKET: weather-raw-data-[your-name]
PROCESSED_BUCKET: weather-processed-data-[your-name]


Set timeout to 30 seconds
Attach AmazonS3FullAccess policy to its role
Test it


STEP 5: Automate with EventBridge
5.1 Create EventBridge Rule

Go to EventBridge in AWS Console
Click Rules → Create rule
Settings:

Name: weather-collection-schedule
Description: "Triggers weather data collection every 6 hours"
Rule type: Schedule
Click Continue to create rule

5.2 Define Schedule

Schedule pattern: A schedule that runs at a regular rate
Rate expression: 6 hours
Click Next

5.3 Select Target

Target type: AWS service
Select a target: Lambda function
Function: weather-data-collector
Click Next
Click Next again (skip tags)
Review and Create rule

5.4 Test Automation

Your collector Lambda will now run every 6 hours automatically!
Check CloudWatch Logs to see execution history
Check S3 buckets to see data accumulating


STEP 6: Add Simple Analysis (Optional)
6.1 Create Analysis Script

You need first to install:
# Install AWS CLI if you don't have it
pip install awscli

# Configure your credentials
aws configure

It will ask you for:

AWS Access Key ID
AWS Secret Access Key
Region (use the same as your buckets, like us-east-1)

To get your Access Keys:

Go to AWS Console → Your name (top right) → Security credentials
Scroll to "Access keys"
Click "Create access key"
Choose "Command Line Interface (CLI)"
Copy the keys (you only see them once)


Create a Python script locally to analyze your data:

Code in analysis folder
    
Run this script after a few days to see your data trends