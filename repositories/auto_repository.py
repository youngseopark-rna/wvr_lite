from sqlalchemy.orm import sessionmaker
import logging


class AutoDetectedReadOnlyRepository:
    logger = logging.getLogger(__name__)

    def __init__(self, session):
        self.session = session

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

        return cls(session)
