FROM python:3.8
LABEL maintainer="techtrends"

WORKDIR /app

COPY . /app

EXPOSE 3111

RUN pip install -r requirements.txt

RUN python init_db.py

# command to run on container start
CMD ["python", "app.py"]