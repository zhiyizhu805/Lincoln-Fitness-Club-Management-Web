from flask import (Blueprint,Flask, flash, redirect, render_template,
                   request, session, url_for)



customer = Blueprint("customer",__name__,template_folder="templates",static_folder="static",static_url_path='/customer/static', url_prefix='')