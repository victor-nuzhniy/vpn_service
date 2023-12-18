#vpn_service

##Description

###Sensitive data
1. Create in the project root (or obtain from team member) an `.env` file with 
environment variables required by application (data below for an expample). 

SECRET_KEY = 'django-insecure-*t(q3ay=og&+4k4dga_-b-+zj%*!ev!lo%s5x&^&!rie5x@ue^'

ALLOWED_HOSTS=localhost 127.0.0.1

DEBUG=1

DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=a@a.com
DJANGO_SUPERUSER_PASSWORD=admin

CELERY_BROKER_REDIS_URL=redis://localhost:6379
CELERY_RESULT_BACKEND=redis://localhost:6379


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

