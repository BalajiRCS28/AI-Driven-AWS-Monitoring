# AI-Driven-AWS-Monitoring

# Get instances IDs:
aws ec2 describe-instances --region us-east-1 \
	--filters "Name=instance-state-name,Values=running" \
	--query "Reservations[*].Instances[*].InstanceId" \
	--output text
# Create S3 bucket:
aws s3 mb s3://gptresponses23
# Create lambda function:
ls
pip install requests==2.25.1 urllib3==1.26.5 -t .
ls
zip -r9 lambda_function2.zip .
ls
less trust-policy.json
less s3_write_policy.json
# Attach rolls:
aws iam create-role --role-name lambda-execute2 \
	--assume-role-policy-document file://trust-policy.json

aws iam put-role-policy --role-name lambda-execute2 \
	--policy-name S3WriteAccess \
	--policy-document file://s3_write_policy.json

# Create function:
aws lambda create-function --function-name LambdaFunction2 \
	--zip-file fileb://lambda_function2.zip \
	--handler lambda_function2.lambda_handler \
	--runtime python3.8 \
	--role arn:aws:iam::1234567890:role/lambda-execute2

aws iam attach-role-policy --role-name lambda-execute2 \
	--policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
aws iam attach-role-policy --role-name lambda-execute2 \
	--policy-arn arn:aws:iam::aws:policy/CloudWatchReadOnlyAccess

# Allow more time before timeout:
aws lambda update-function-configuration \
	--function-name LambdaFunction2 \
	--timeout 30

# Invoke function test:
aws lambda invoke --function-name LambdaFunction2 output.txt

# Update
aws lambda update-function-code --function-name LambdaFunction2 \
	--zip-file fileb://lambda_function2.zip

# Open GUI

# Download response:
aws s3 ls gptresponses23/
aws s3 cp s3://gptresponses23/gpt_analysis.txt .

