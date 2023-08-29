from app import app
from layouts import Layout
from callbacks import *

app.layout = Layout
server = app.server
if __name__ == '__main__':
    app.run_server(debug=False)