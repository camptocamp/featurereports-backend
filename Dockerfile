########################
# Build frontend #
########################
FROM node:12-slim as front-server

COPY app/drealcorsereports/static/admin/package-lock.json app/drealcorsereports/static/admin/package.json /app/
WORKDIR /app
RUN npm install
ENV PATH="$PATH:/app/node_modules/.bin"
# Save /app/node_modules from being masked by another volume
VOLUME /app/node_modules
COPY app/drealcorsereports/static/admin/ /app/
EXPOSE 3000
CMD npm start

FROM front-server as front-builder
RUN npm run build

##########################################
# Common base for build/test and runtime #
##########################################
FROM python:3.9-slim AS base

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
COPY app/requirements.txt /app/requirements.txt
RUN pip3 install --disable-pip-version-check --no-cache-dir -r /app/requirements.txt && \
  rm --recursive --force /tmp/* /var/tmp/* /root/.cache/*


########################
# Build and test image #
########################
FROM base AS tools

RUN apt-get update && apt-get install -y \
    curl \
    make

COPY app/requirements-dev.txt /tmp/
RUN pip3 install --disable-pip-version-check --no-cache-dir -r /tmp/requirements-dev.txt && \
  rm --recursive --force /tmp/* /var/tmp/* /root/.cache/*

WORKDIR /app
COPY app /app/
COPY Makefile .
RUN pip3 install --no-deps -e .
COPY --from=front-builder /app/build /opt/drealcorsereports/static/admin/build

CMD make test && make front-test


#################
# Runtime image #
#################
FROM base AS app
LABEL maintainer Camptocamp "info@camptocamp.com"

WORKDIR /app
COPY --from=tools /app/ /app/
RUN pip install --no-deps -e .
COPY --from=front-builder /app/build /opt/drealcorsereports/static/admin/build
ENV PROXY_PREFIX=
EXPOSE 8080
CMD alembic upgrade head && pserve c2c://${INI_FILE}