# pull official base image
FROM python

# set work directory
WORKDIR /app

COPY ./requirements.txt .
RUN pip install -r requirements.txt

# copy project
COPY . .

# Ustaw zmienną środowiskową
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Expose the port
EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]