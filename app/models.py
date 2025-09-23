from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime, timezone
#model of how the datatable looks
class Expense(Base):
    __tablename__ = "expenses"
    id= Column(Integer, primary_key=True, index=True)
    amount = Column(Numeric(10,2), nullable=False)
    currency= Column(String(3), default="USD")
    category=Column(String(50),default = "uncategorized" )
    description = Column(String(255), nullable = True)
    occurred_at = Column(DateTime, default=datetime.now(timezone.utc))
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    payment_method = Column(String(50), default="cash")
      # ← THIS IS NEW / CRITICAL
    user_id = Column(Integer, ForeignKey("users.id"))  # link to User
    user = relationship("User", back_populates="expenses")  # link back to User

#ForeignKey & relationship: connects expenses to users → allows multi-user apps.
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username=Column(String(50), unique=True, index=True, nullable=False)
    hashed_password= Column(String, nullable=False)

    expenses = relationship("Expense", back_populates="user") #Linked expenses to users via user_id + relationship

print("this is a test")
