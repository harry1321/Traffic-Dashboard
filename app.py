import dash
from layouts import Layout

app = dash.Dash(__name__, suppress_callback_exceptions=True)
from callbacks import *
app.layout = Layout
server = app.server