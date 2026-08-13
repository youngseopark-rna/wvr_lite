from sqlalchemy import Column, String, Float, Integer, DateTime
from tables import BaseModel, ALM_SCENARIO, A_COMPANY, STEP_DATE, ASSETS_TOTAL, BE_LIABILITY, VALUE_MARKET

class A_Company(BaseModel):
    __tablename__ = A_COMPANY

    step_date = Column(STEP_DATE, DateTime, primary_key=True)
    alm_scenario = Column(ALM_SCENARIO, Integer)
    be_liability = Column(BE_LIABILITY, Float)
    value_market = Column(VALUE_MARKET, Float)