from app import app
from layouts import Layout
from callbacks import *

app.layout = Layout

if __name__ == '__main__':
    app.run_server(debug=False)