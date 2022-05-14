# Install the base requirements for the app.
# This stage is to support development.
FROM python:3.9 AS base
WORKDIR .
COPY requirements.txt .
RUN /usr/local/bin/python -m pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 8000/tcp
EXPOSE 8000/udp

COPY . ./ADS-PIII

# Install OpenJDK-17
RUN apt-get update && \
    apt-get install -y openjdk-17-jdk && \
    apt-get install -y ant && \
    apt-get clean;
    
# Fix certificate issues
RUN apt-get update && \
    apt-get install ca-certificates-java && \
    apt-get clean && \
    update-ca-certificates -f;

#RUN python ADS-PIII/manage.py migrate 
#RUN python ADS-PIII/manage.py runserver 0.0.0.0:8000
