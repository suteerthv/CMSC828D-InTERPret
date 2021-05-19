# pull official base image
FROM python:3.8.0-alpine
# set work directory
WORKDIR /usr/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev libxml2-dev libxslt clang

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt /usr/app/requirements.txt
RUN export LDFLAGS="-L/usr/local/opt/openssl/lib"
RUN pip install -r requirements.txt

# copy project
EXPOSE 5000
RUN ls -la /usr/app/src
ENTRYPOINT ["sh", "/usr/app/src/docker-entrypoint.sh"]
