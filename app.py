from flask import (Flask)

app = Flask(__name__)
app.secret_key = "admin123" 

# Registering blueprints

if __name__ == '__main__':
    app.run(debug=True)
