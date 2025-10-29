FROM python:3.12-slim

# Metadata
ENV PYTHONUNBUFFERED=1 PIP_BREAK_SYSTEM_PACKAGES=1

# Install system dependencies in one step, clean cache to reduce size
RUN apt-get update -y && \
  apt-get install -y --no-install-recommends \
  build-essential graphviz graphviz-dev netcat-openbsd libpq-dev && \
  apt-get clean && rm -rf /var/lib/apt/lists/*

# Create working directories
RUN mkdir /code

# Set permissions and create a non-root user
ARG USER_ID=1000
ARG GROUP_ID=1000
RUN groupadd -g $GROUP_ID appgroup && \
  useradd -u $USER_ID -g appgroup -m appuser
USER appuser

WORKDIR /ims

# Copy requirements and install as non-root user
COPY --chown=appuser:appgroup ./config/pip-requirements.txt /code/
RUN pip install --user -r /code/pip-requirements.txt

# Copy scripts
COPY --chown=appuser:appgroup start_django_server.sh /code/

# Entrypoint or CMD can be added here

