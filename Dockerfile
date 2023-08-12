FROM public.ecr.aws/lambda/python:3.10
# Copy function code
COPY . ${LAMBDA_TASK_ROOT}
# Install the function's dependencies using file requirements.txt
# from your project folder.
RUN pip3 install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu --target="${LAMBDA_TASK_ROOT}"

COPY requirements.txt .

RUN pip3 install --no-cache-dir  -r requirements.txt --target="${LAMBDA_TASK_ROOT}"

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "app.handler" ]