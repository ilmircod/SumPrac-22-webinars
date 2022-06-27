# share_service

### Up and build containers
```shell
docker-compose up -d --build
```

### Locally run celery with beat
```shell
celery -A share_service worker -B -l INFO
```


### Locally run flower
```shell
flower -A share_service --port=5555
```


### Create (or update) a message file in the conf/locale (in the django tree) or locale (for projects and applications) directory
```shell
django-admin makemessages -i staticfiles -l ru
```

### Compile .po files to .mo files for use with builtin gettext support
```shell
django-admin compilemessages
```