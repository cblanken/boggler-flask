FROM python:3.10-alpine

ENV FLASK_APP main.py

# Setup non-root account
RUN adduser -D boggler
USER boggler
WORKDIR /home/boggler

# Copy necessary files
COPY requirements requirements
COPY wordlists wordlists
COPY app app
COPY main.py boot.sh ./

# Setup virtualenv
RUN python -m venv venv

# Install dependencies
RUN venv/bin/pip install -r requirements/docker.txt

# Runtime configs
EXPOSE 5000
ENTRYPOINT ["./boot.sh"]
