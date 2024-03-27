from flask import (Blueprint,Flask, flash, redirect, render_template,
                   request, session, url_for)



traniner = Blueprint("traniner",__name__,template_folder="templates",static_folder="static",static_url_path='/traniner/static', url_prefix='')