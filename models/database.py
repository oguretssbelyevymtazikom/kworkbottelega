from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


# _Engine = create_engine('mysql+pymysql://gen_user:mysqlPassl001@89.223.69.226/default_db')
_Engine = create_engine('sqlite+pysqlite:///database.db')
_Session = sessionmaker(bind=_Engine)
_Base = declarative_base()
_db = _Session()
