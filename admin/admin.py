from flask import (Blueprint,Flask, flash, redirect, render_template,
                   request, session, url_for)



admin = Blueprint("admin",__name__,template_folder="templates",static_folder="static",static_url_path='/admin/static', url_prefix='')