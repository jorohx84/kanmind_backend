1.Create and activate a virtual environment

python3 -m venv env
source env/bin/activate 


2.Install dependencies

pip install -r requirements.txt


3.Apply database migrations

python manage.py migrate


4.Start the development server:

python manage.py runserver
