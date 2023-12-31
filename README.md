#vpn_service

##Description

###Sensitive data
1. Create in the project root (or obtain from team member) an `.env` file with 
environment variables required by application (data below for an expample). 

SECRET_KEY = 'django-insecure-*t(q3ay=og&+4k4dga_-b-+zj%*!ev!lo%s5x&^&!rie5x@ue'

POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=vpn

ALLOWED_HOSTS=localhost 127.0.0.1

DEBUG=1

DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=a@a.com
DJANGO_SUPERUSER_PASSWORD=admin

CELERY_BROKER_REDIS_URL=redis://vpn_service-redis-1:6379
CELERY_RESULT_BACKEND=redis://vpn_service-redis-1:6379

### Performing commits

1. Pre-commit hook installed, settings are in .pre-commit-config.yaml
2. To instantiate new hook settings change .pre-commit-config.yaml file
     and run     pre-commit install
3. To bypass hook checking run      git commit -m "..." --no-verify

### Redis

1. We will use a celery that's in turn uses Redis. 
    To start a Redis server on port 6379, we can run the following command:
        docker run -p 6379:6379 -d redis:5

### Celery

1. To run celery use command in terminal
    celery -A config worker -l -P solo (-P solo or --pool=solo for Windows)
2. To run beat service use command in terminal
    celery -A config beat
3. To upgrade celery settings run
    celery upgrade settings config/settings.py
4. To delete task from the queue
    celery -A config purge


###Running service locally.
1. Using docker-compose HOST can be 127.0.0.1:8000 (gunicorn will be run on that host
   and port) or 127.0.0.1 - nginx is configured that way.
2. Running with virtual env postgres host and port should be changed with localhost
   and 8778 respectfully, celery .env host settings should be changed to localhost.


### Project installation steps with docker locally

1. Clone project.
2. Create .env file with info descripted earlier in this file.
3. Run command 
    docker-compose up redis
4. Host in redis .env statements should be checked and setted with container ip or name
   (172.18.0.2 or 172.18.0.3 can be got with command
    docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' container_name_or_id)
    or can be used name (for example - vpn_service-redis-1 - depends on the system)
5. Run command docker-compose up (you can use second terminal)
6. Try app with domain http://127.0.0.1
