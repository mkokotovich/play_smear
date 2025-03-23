FROM node:22.14 as uibuilder

# set working directory
WORKDIR /usr/src/app

COPY ui/yarn.lock /usr/src/app/yarn.lock
COPY ui/package.json /usr/src/app/package.json
COPY ui/config-overrides.js /usr/src/app/config-overrides.js
ENV PATH $PATH:/usr/src/app/node_modules/.bin/
RUN yarn install

COPY ui .

RUN yarn build

#=============================================

FROM python:3.13-slim

ENV PYTHONUNBUFFERED 1

WORKDIR /usr/src/app
COPY ./backend/requirements.txt .
RUN pip install -r requirements.txt

COPY backend .

RUN mkdir -p /static/www/
COPY --from=uibuilder /usr/src/app/build /static/www/

RUN python manage.py collectstatic --noinput --clear

EXPOSE 8000

CMD ["gunicorn", "api.wsgi", "-c", "gunicorn.conf.py"]
