FROM python:3
ADD my_script.py /
ADD config.py /
ADD resource.csv /
ADD app /app
RUN easy_install pip
RUN pip install flask
RUN pip install flask_restful
RUN pip install flask_sqlalchemy
RUN python -m easy_install pbkdf2
RUN pip install flask-mail
RUN apt-get update && apt-get install netcat -y
CMD [ "python", "./my_script.py" ]
