# pull base image
FROM python:3.7

# set work directory
WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# copy Pipfile
COPY Pipfile /app/
COPY Pipfile.lock /app/

# install dependencies
RUN apt-get update; apt-get install -y netcat
RUN pip install pipenv
RUN pipenv install --system --deploy

# run entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]
