# Use a standard debian image
FROM debian:latest

# Run updates and install pip,python,curl
RUN apt-get update && apt-get install -y \
	curl \
	python-pip \
	build-essential


# Copy the python app and set the directory.
COPY . /hw2
WORKDIR /hw2/hw2

COPY . /hw2
WORKDIR /hw2/hw2

# Install Flask
RUN pip install -r flaskcheck.txt
RUN pip install requests

# Change command to run python scripts
CMD ["python","node.py"]
