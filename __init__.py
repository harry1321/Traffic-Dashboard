from app import app
from layouts import Layout
from callbacks import *
#from layouts import sales, page2, page3

app.layout = Layout

if __name__ == '__main__':
    app.run_server(debug=True)