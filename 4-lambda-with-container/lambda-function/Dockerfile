FROM amazon/aws-lambda-python:latest
COPY app.py requirements.txt ./
RUN pip install -r requirements.txt
CMD [ "app.main" ]
