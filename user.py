#
# user database:
#
# - adding a database to manager the users
#
# DATE:  1/25/26
#
# TODO:
#
# - brain storming phase, no implementation yet.
#


from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime

class User(Base):
    __tablename__ = "user"
    
    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)



