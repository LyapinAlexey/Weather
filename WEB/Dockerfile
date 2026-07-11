FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt
COPY config.py /app
COPY services.py /app
COPY models.py /app
COPY dbclear.py /app
COPY logging_config.py /app
COPY schemas.py /app
COPY WEB/app.py /app
COPY WEB/static /app/static
COPY WEB/templates /app/templates
COPY alembic /app/alembic
COPY alembic.ini /app
CMD ["gunicorn", "app:app", "-w", "4", "-b", "0.0.0.0:5001"]   