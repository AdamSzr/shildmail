# pull official base image
FROM python

# set work directory
WORKDIR /usr/src/app

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# copy project
COPY . .

# Expose the port
EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]