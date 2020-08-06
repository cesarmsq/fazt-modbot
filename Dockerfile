FROM python:3.8.3-alpine

COPY entrypoint.sh .

WORKDIR /app

COPY Pipfile Pipfile.lock ./

ENV PIP_NO_CACHE_DIR=1

RUN apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev git && \
    pip install pipenv --no-cache-dir && \
    pipenv install --system --deploy --ignore-pipfile

COPY . .

RUN pip install -e .

RUN chmod +x entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
