##########################################
# Common base for build/test and runtime #
##########################################
FROM python:3.9-slim AS base

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
COPY ./requirements.txt /app/requirements.txt
RUN pip3 install --disable-pip-version-check --no-cache-dir -r /app/requirements.txt && \
  rm --recursive --force /tmp/* /var/tmp/* /root/.cache/*


########################
# Build and test image #
########################
FROM base AS tools

RUN apt-get update && apt-get install -y \
    curl \
    make

COPY requirements-dev.txt /tmp/
RUN pip3 install --disable-pip-version-check --no-cache-dir -r /tmp/requirements-dev.txt && \
  rm --recursive --force /tmp/* /var/tmp/* /root/.cache/*

WORKDIR /app
COPY . /app/
RUN pip3 install --no-deps -e .

CMD ["make"]


#################
# Runtime image #
#################
FROM base AS app
LABEL maintainer Camptocamp "info@camptocamp.com"

WORKDIR /app
COPY --from=tools /app/ /app/
RUN pip install --no-deps -e .

ENV PROXY_PREFIX=
