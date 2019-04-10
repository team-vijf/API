FROM python:3-alpine

WORKDIR /usr/src/app

RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 80

COPY . .

CMD [ "python", "-u", "./app.py" ]