<h1 align="center">Email Sender Using Javascript, Python, Strip, Paypal, and Redis</h1>

<p align="center"> <a href="https://www.w3schools.com/css/" target="_blank"> <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/css3/css3-original-wordmark.svg" alt="css3" width="40" height="40"/> </a> <a href="https://www.djangoproject.com/" target="_blank"> <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/django/django-original.svg" alt="django" width="40" height="40"/> </a> <a href="https://www.w3.org/html/" target="_blank"> <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/html5/html5-original-wordmark.svg" alt="html5" width="40" height="40"/> </a> <a href="https://developer.mozilla.org/en-US/docs/Web/JavaScript" target="_blank"> <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/javascript/javascript-original.svg" alt="javascript" width="40" height="40"/> </a> <a href="https://www.python.org" target="_blank"> <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/python/python-original.svg" alt="python" width="40" height="40"/> </a> </p>
<p align="center"><img width="100%" src="https://github.com/iMiebaka/ProjectRaven/blob/main/homepage.png" alt="send_email"></p>

- This web app lets you send email(s) more than 200 recievers. Some email services will block you, but you can also add more sender emails so the email service wouldn't flag your account for spamming.

## Required software installation on Linux/Unix (Version >=6)

```shell
sudo apt update
sudo apt-get install redis-server python-dev3 python3-pip git
redis-cli -v #verfiy the version
systemctl start redis #start redis
sudo systemctl enable redis #run redis on boot up
```

## Download this code to your machine

- Use this command below to clone this git repo on your machine

```shell
git clone https://github.com/iMiebaka/ProjectRaven.git
```

## Run the following command to create the file a settings.ini file

- In the root directory, make a settings.ini to hold all your sensative data like: strip cred, admin email and password etc. Run the code below on a terminal to create the file.

```shell
nano settings.ini
```

- Add the following code below to the setting.ini file (And make neccessary modifications)

```shell
[settings]
SECRET_KEY=<generate a django secret key>
STRIPE_PUBLISHABLE_KEY=<strip publishable key>
STRIPE_SECRET_KEY=<sripe secret key>
STRIPE_ENDPOINT_SECRET=<sripe secret endpoint>
PRODUCT_TAG=<product tag>
EMAIL_HOST_USER=<admin validation email>
EMAIL_HOST_PASSWORD=<admin validation password>
DEFAULT_FROM_EMAIL=Lenollo< <admin validation email> >
```

Install all dependencies required

```shell
pip install -r requirements.txt
```

- Run the Django app on the console

```shell
python manage.py runserver 0:8000
```

- Run Celery Celery Beat on two seperate terminal respectively

```shell
celery -A mailer_system worker -l INFO
celery -A mailer_system beat -l INFO
```

- Run stripe webhook on another terminal

```shell
./stripe listen --forward-to localhost:8000/payments/webhook/
```

- <a href="http://localhost:8000" target="_b" rel="noopener noreferrer"> Open the app on localhost</a>

## Preparing the Sender and Reciever Document

Before you are able to send mail, you have to be on an active subscription plan, and payments can be made either through strip, paypal or credit/debit card

<p align="center"><img width="100%" src="https://github.com/iMiebaka/ProjectRaven/blob/main/subscription_page.png" alt="make_payment"></p>

- To send any email, the sender and reciever credential should be in a document files. Document recognised by this app should either be a .csv and .xlmx files extension. This Document files should be seperate from each other and must have a header tag (else an error will be raised)

<br>
<strong>Reciever Email Document Template</strong>

<table>
    <thread>
        <tr>
            <th>email</th>
        </tr>
    </thread>
    <tbody>
        <tr>
            <td>ujanet@kentel.buzz</td>
            <td>1111@gmail.com</td>
            <td>2222@gmail.com</td>
            <td>3333@gmail.com</td>
            <td>4444@gmail.com</td>
        <tr>
    <tbody>
</table>

<br>
<strong>Sender Email and Password Document Template</strong>
<table>
    <thread>
        <tr>
            <th>email</th> 
            <th>password</th>
        </tr>
    </thread>
    <tbody>
        <tr>
            <td>d360@gmail.com</td>
            <td>XXXXXX</td>
        </tr>
    </tbody>
</table>

- You can have as many sender and receiver emails, the backend algorithm is optimized to handled the requst properly.

## Hosting

I recommend you run this code on a linux VPS like
<a href="https://digitalocean.com" target="_b" rel="noopener noreferrer">Digital Ocean</a> or
<a href="https://linode.com" target="_b" rel="noopener noreferrer">Linode</a>
This kind of vps provide more flexibility especially for services like Redis, and Stripe Webhook.
<br>
<strong>NB:</strong> Before deploying this projects to production, ensure you comment the EMAIL_BACKEND for development and uncomment the EMAIL_BACKEND for deployment. This will enable use the smtp instead of displaying emails on the console.