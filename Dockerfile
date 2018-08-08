
# Python support can be specified down to the minor or micro version
# (e.g. 3.6 or 3.6.3).
# OS Support also exists for jessie & stretch (slim and full).
# See https://hub.docker.com/r/library/python/ for all supported Python
# tags from Docker Hub.
FROM python:alpine

# If you prefer miniconda:
#FROM continuumio/miniconda3

# RUN adduser -D spotlight

# LABEL Name=spotlight Version=0.0.1
# EXPOSE 5000

# # WORKDIR /app
# WORKDIR /home/spotlight


# ADD . /app

# # Using pip:
# RUN python3 -m pip install -r requirements.txt
# RUN python3 -m pip install gunicorn
# COPY spotlight.py boot.sh ./
# RUN chmod +x boot.sh

# ENV FLASK_APP spotlight.py
# CMD ["python3", "-m", "spotlight"]


# ENTRYPOINT ["./boot.sh"]

# Using pipenv:
#RUN python3 -m pip install pipenv
#RUN pipenv install --ignore-pipfile
#CMD ["pipenv", "run", "python3", "-m", "spotlight"]

# Using miniconda (make sure to replace 'myenv' w/ your environment name):
#RUN conda env create -f environment.yml
#CMD /bin/bash -c "source activate myenv && python3 -m spotlight"

#################################################################################################################################

RUN adduser -D spotlight

WORKDIR /home/spotlight

COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn

COPY app app
COPY spotlight.py  boot.sh ./
RUN dos2unix boot.sh
RUN chmod +x boot.sh

ENV FLASK_APP spotlight.py

RUN chown -R spotlight:spotlight ./
USER spotlight

EXPOSE 5000
#RUN source venv/bin/activate
#RUN flask translate compile
#RUN gunicorn -b :5000 
ENTRYPOINT ["./boot.sh"]