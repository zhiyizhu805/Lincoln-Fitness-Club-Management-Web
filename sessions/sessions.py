from flask import (Blueprint,Flask, flash, redirect, render_template,
                   request, session, url_for)



auth = Blueprint("sessions",__name__,template_folder="templates",static_folder="static",static_url_path='/sessions/static', url_prefix='')