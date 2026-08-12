from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker
import logging

class AutoDetectedReadOnlyRepository:
    logger = logging.getLogger(__name__)

    def __init__(self, session, base):
        self.session = session
        self.base = base

    @classmethod
    def create(cls, engine):
        # create session for db connection
        try:     
            session_maker = sessionmaker(bind=engine)
            session = session_maker()
            cls.logger.info(f"Successfully created DB Session: {session}")
        except Exception as e:
            cls.logger.exception(f"Failed to create DB Session: {e}")
            raise RuntimeError from e

        # create base for auto detection of tables
        try:
            base = automap_base()
            base.prepare(autoload_with=engine)
        except Exception as e:
            cls.logger.exception(f"Failed to create AutoMap Base: {e}")
            raise RuntimeError from e
        
        return cls(session, base)