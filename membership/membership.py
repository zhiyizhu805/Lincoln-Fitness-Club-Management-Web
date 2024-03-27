from flask import (Blueprint,Flask, flash, redirect, render_template,
                   request, session, url_for)



membership = Blueprint("membership",__name__,template_folder="templates",static_folder="static",static_url_path='/membership/static', url_prefix='')