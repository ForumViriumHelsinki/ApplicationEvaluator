# pull base image
FROM python:3.11

# set work directory
WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH /app/

# copy Pipfile
COPY Pipfile /app/
COPY Pipfile.lock /app/

# install dependencies
RUN apt-get update; apt-get install -y ncat
RUN pip install pipenv
RUN pipenv install --system --deploy

# run entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]
