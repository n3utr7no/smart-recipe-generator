# run.py
from dotenv import load_dotenv
load_dotenv() # This must be at the very top to load your .env file

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)