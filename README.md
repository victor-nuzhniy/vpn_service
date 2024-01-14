#vpn_service

##Description
1. Project create vpn service with proxy server to count loaded and sended data,
    page transition count for particular domain.
2. To use project functionality you should sign up and login.
3. Afterwards you create site entry with domain name and scheme.
4. With click on created link you can serve site in vpn mode with all that 
    functionality above.
5. All site links will be substituted with http://127.0.0.1/localhost/domain/...
6. With external link you will leave the service.

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

CELERY_BROKER_REDIS_URL=redis://redis_vpn:6379
CELERY_RESULT_BACKEND=redis://redis_vpn:6379

### Performing commits

1. Pre-commit hook installed, settings are in .pre-commit-config.yaml
2. To instantiate new hook settings change .pre-commit-config.yaml file
     and run     pre-commit install
3. To bypass hook checking run      git commit -m "..." --no-verify

### Redis

1. We will use a celery that's in turn uses Redis (locally). 
    To start a Redis server on port 6379, we can run the following command:
        docker run -p 6379:6379 -d redis:5

### Celery

1. To run celery use command in terminal
    celery -A config worker -l -P solo (-P solo or --pool=solo for Windows)
2. To upgrade celery settings run
    celery upgrade settings config/settings.py
3. To delete task from the queue
    celery -A config purge


###Running service locally.
1. Using docker-compose  127.0.0.1 - nginx is configured that way.
2. Running with virtual env postgres host and port should be changed with localhost
   and 8778 respectfully, celery .env host settings should be changed to localhost.
3. Also change celery_broker_redis_url and celery_result_backend host to localhost.


### Project installation steps with docker locally

1. Clone project.
2. Create .env file with info descripted earlier in this file.
3. Run command 
    docker-compose up
6. Try app with domain http://127.0.0.1
