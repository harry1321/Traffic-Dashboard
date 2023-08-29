import dash
from layouts import Layout
from callbacks import *

app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.layout = Layout
server = app.server