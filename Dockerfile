from python:3.8

# Make app directory
RUN mkdir /app
WORKDIR /app/

# Install requirements
COPY poetry.lock pyproject.toml /app/
RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev

# Add in app code
COPY todoscreens/ /app/todoscreens

# Run a server
CMD ["gunicorn", "--bind=0.0.0.0:8080", "todoscreens:app"]
