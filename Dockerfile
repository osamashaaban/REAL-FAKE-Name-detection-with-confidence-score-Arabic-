# Select Python Version
FROM python:3.10.7
# Create work directory inside docker
WORKDIR /home/python/api
# Copy api folder from current directory into "/home/python/api" --> which is inside docker
COPY api /home/python/api/
# Image build setup
RUN pip install -r requirements.txt
# When running docker-compose up this command will run this "FileName.py"
#  after launching the image file using "docker build -t {Image_Name} . "
CMD python webserver.py