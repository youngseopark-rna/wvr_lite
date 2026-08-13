from sqlalchemy.orm import declarative_base

ALM_SCENARIO = "ALM Scenario"
A_COMPANY = "A_Company"
STEP_DATE = "Step Date"
ASSETS_TOTAL = "Assets_Total"
BE_LIABILITY = "BE_Liability"
VALUE_MARKET = "Value_Market"

Base = declarative_base()

class BaseModel(Base):
    __abstract__ = True

    def __repr__(self):
        table_name = getattr(self, "__tablename__", self.__class__.__name__)

        columns = [
            f"{col.name}={repr(getattr(self, col.name))}"
            for col in self.__table__.columns
        ]

        return f"<{table_name}({', '.join(columns)})>"