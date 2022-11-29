# set the base image
# n/b: for production, node is only used for building
# the static Html and javascript files
# as react creates static html and js files after build
# these are what will be served by nginx
# use alias build to be easier to refer this container elsewhere
# e.g inside nginx container
FROM node:16
# set working directory
# this is the working folder in the container
# from which the app will be running from
WORKDIR /app
# add the node_modules folder to $PATH
ENV PATH /app/node_modules/.bin:$PATH
COPY package.json tsconfig.json yarn.lock /app/
RUN yarn install --network-timeout=30000
