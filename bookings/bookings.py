from flask import (Blueprint,Flask, flash, redirect, render_template,
                   request, session, url_for)



bookings = Blueprint("bookings",__name__,template_folder="templates",static_folder="static",static_url_path='/bookings/static', url_prefix='')