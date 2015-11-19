FROM frolvlad/alpine-python3
RUN pip3 install gunicorn django --no-cache-dir
ADD . .
WORKDIR lo01testy
EXPOSE 5000
CMD gunicorn -w 4 -b 0.0.0.0:5000 lo01testy.wsgi:application
