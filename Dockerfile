FROM python:3.8

COPY requirements.txt /opt/app/requirements.txt
WORKDIR /opt/app
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . /opt/app
RUN ls
RUN ls src

CMD ["python", "src/main.py"]