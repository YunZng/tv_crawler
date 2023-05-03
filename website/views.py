from flask import Blueprint, render_template, request
from .tv_crawler import run


views = Blueprint('views', __name__)

# the following func runs everytime we the route is opened, methods includes the type of acceptable requests
@views.route('/', methods=['GET', 'POST'])
def home():
    # get data from the post request
    title=''
    cast=''
    general=''
    everything=''
    if request.method == 'POST':
        data = request.form
        button = data.get('button')
        if button == 'search':
            title = data.get('title')
            cast = data.get('cast')
            general = data.get('general')
        if button == 'test':
            title = data.get('title')
            cast = data.get('cast')
            general = data.get('general')
            everything = run()
    # u can also pass variables in this function
    return render_template('home.html', title=title, cast=cast, general=general, everything=everything)

# This file is a blue print for our views, we need to register them in __init__.py