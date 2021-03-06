###Tutorial for using Celery with RabbitMQ

####Getting Started

Clone and cd into the repo, then install RabbitMQ if you haven't already:

```bash
$ brew install rabbitmq
```

Run the server as a background process and set up user and vhost:

```bash
$ sudo rabbitmq-server -detached
$ sudo rabbitmqctl add_user [USERNAME] [PASSWORD]
$ sudo rabbitmqctl add_vhost [VHOST_NAME]
$ sudo rabbitmqctl set_permissions -p [VHOST_NAME] [USERNAME] ".*" ".*" ".*"
```

Activate the virtual env and get the dependencies:

```bash
$ virtualenv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```

Get the server and worker running:

```
$ python server.py
$ celery -A server.celery worker --loglevel=info
```

Check out the blog post [here](http://suzannewang.com/celery-rabbitmq-tutorial/).