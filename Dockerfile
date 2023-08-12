FROM public.ecr.aws/lambda/python:3.10
# Copy function code
RUN pip install -U pip

RUN pip3 install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

COPY . .

RUN pip3 install --no-cache-dir  -r requirements.txt

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "app.lambda_handler" ]