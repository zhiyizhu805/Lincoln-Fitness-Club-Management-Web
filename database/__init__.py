from .db_manager import DatabaseManager
from .connect import dbuser, dbpass, dbhost, dbport, dbname

db_manager = DatabaseManager(host=dbhost, user=dbuser, password=dbpass, database=dbname)