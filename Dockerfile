FROM python:3.10-alpine

ENV FLASK_APP main.py

# Setup virtualenv
RUN pip install poetry;

# Setup non-root account
RUN adduser -D boggler;
USER boggler
WORKDIR /home/boggler

# Copy necessary files
COPY requirements.txt requirements.txt
COPY pyproject.toml pyproject.toml
COPY poetry.lock poetry.lock
COPY wordlists wordlists
COPY --chown=boggler:boggler app app
COPY --chown=boggler:boggler data data
COPY config config
COPY main.py boot.sh ./

# Install dependencies
RUN poetry install

# Runtime configs
EXPOSE 5000
ENTRYPOINT ["./boot.sh"]
