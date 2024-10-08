FROM python:3.13

# Install build essentials and PostgreSQL development libraries
RUN apt-get update && \
    apt-get install -y build-essential libpq-dev postgresql-client --no-install-recommends && \
    rm -rf /var/lib/apt/lists/* || { cat /var/log/apt/term.log; exit 1; }

# Upgrade pip and setuptools
RUN python -m pip install --upgrade pip setuptools

# Install psycopg2-binary to avoid compilation during the build
RUN python -m pip install psycopg2-binary

# Install other dependencies from requirements.txt
COPY . .
RUN python -m pip install -r requirements.txt

# Create a non-root user (optional)
RUN useradd -m myuser
USER myuser

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
