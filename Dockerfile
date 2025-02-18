FROM python:3.13.2-alpine

WORKDIR /app

COPY . /app/

RUN pip3 install --upgrade pip && pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

EXPOSE 5000

CMD ["gunicorn", "wsgi:application", "-b", "0.0.0.0:5000", "-w", "4"]
