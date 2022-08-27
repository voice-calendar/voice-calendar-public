# Acsent Calendar

## About
A calendar that allows users to create Google Calendar events using their voice. It uses Alan AI for the voice software, Google Cloud API for the calendar, and Django for the app. 

## Setup for Development Purposes

Based on [a tutorial by Simple Is Better Than Complex](https://simpleisbetterthancomplex.com/series/2017/09/04/a-complete-beginners-guide-to-django-part-1.html).
(Some instructions from the tutorial are changed because you are downloading the Django project instead of making one from scratch.)

1. Download Python 3.10.5 (should come with pip3)

2. Install the virtual environment. In Terminal do `sudo pip3 install virtualenv` for Mac users

3. Create a folder. In terminal, `cd` to the folder and create and activate a virtual environment:
```
virtualenv venv -p python3
source venv/bin/activate
```
If it worked, the terminal prompt should have `(venv)` at the beginning. 

4. Install Django (does not work with version 4.1): 
```
pip3 install Django==4.0.6
```

5. Clone this repository inside the folder from step 3. 

6. Install the necessary modules using `pip3 install MODULE_NAME_HERE`. Below are the module names. 
  * django-extensions  
  * django-widget-tweaks  
  * google-apis-oauth-django  
  * google-api-python-client  
  * python-dateutil  
  * Werkzeug
  * pyOpenSSL

7. Copy the contents of production.py to a file called development.py in the same folder. Generate a Django secret key and place it in the slot in development.py (where it says `os.environ['SECRET_KEY']`). Change `DEBUG` to `True` for testing purposes. 

8. Set up a Google Calendar API on Google Cloud. Download the OAuth ID as a JSON. In views.py, update `JSON_FILEPATH` to the path to this JSON file. 

9. To check if it is working so far, `cd` to the repository folder and do `python3 manage.py runserver`. If there are no errors and you can see the website at http://127.0.0.1:8000/, it is working so far. 

### Getting https on localhost
Although you can see the website, the Google OAuth sign-in does not work under http, so you will not be able to sign in. To get https on localhost, follow [this tutorial by freeCodeCamp](https://www.freecodecamp.org/news/how-to-get-https-working-on-your-local-development-environment-in-5-minutes-7af615770eec/). Afterwards, instead of `python3 manage.py runserver` do `python3 manage.py runserver_plus --cert-file YOUR_FILE_PATH/server.crt --key-file YOUR_FILE_PATH/server.key`. To access the website go to https://localhost:8000.
  
If something isn't working, feel free to email us at acsentmusic@gmail.com. 
