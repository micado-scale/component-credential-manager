FROM python:3-slim

RUN easy_install pip
RUN pip install flask
RUN pip install flask_restful
RUN pip install flask_sqlalchemy
RUN python -m easy_install pbkdf2
RUN pip install flask-mail
RUN pip install flask-script
RUN pip install flask-user

ADD main_script.py /opt/credential-manager/main_script.py
ADD resource.csv /opt/credential-manager/resource.csv
ADD app /opt/credential-manager/app
ADD lib /opt/credential-manager/lib

RUN apt-get update && apt-get install netcat -y && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/credential-manager/
CMD [ "python", "/opt/credential-manager/main_script.py" ]
