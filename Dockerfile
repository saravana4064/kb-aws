FROM public.ecr.aws/lambda/python:3.11

# Install dependencies
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Copy your app code
COPY main.py .

# Set the Lambda handler
CMD ["main.lambda_handler"]