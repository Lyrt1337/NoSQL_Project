FROM python:3.11-alpine

RUN apk update && apk add --no-cache curl bash

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# load wait-for-it.sh-script
RUN curl -o /usr/local/bin/wait-for-it.sh https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh \
    && chmod +x /usr/local/bin/wait-for-it.sh

# execute init_script.py and start flask-app
CMD ["/usr/local/bin/wait-for-it.sh", "mongodb:27017", "--", "python", "/app/init_script.py", "&&", "python", "/app/app.py"]
