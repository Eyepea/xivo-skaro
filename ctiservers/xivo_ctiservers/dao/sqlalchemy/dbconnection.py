from sqlalchemy.engine import create_engine
from sqlalchemy.orm.session import sessionmaker
class DBConnection(object):
    
    _session = None
    
    def __init__(self, uri):
        self._uri = uri
    
    def connect(self):
        self._engine = create_engine(self._uri)
        Session = sessionmaker(bind=self._engine)
        DBConnection._session = Session()
    
    def getEngine(self):
        return self._engine
        
    @staticmethod
    def getSession():
        return DBConnection._session