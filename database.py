from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

class Posting(Base):
    __tablename__ = "postings"

    id = Column(Integer, primary_key=True)
    
    source= Column(String)
    company= Column(String)
    position= Column(String)
    location= Column(String)
    description= Column(String)
    pay = Column(String)
    url = Column(String)
    first_seen = Column(DateTime)

class UserInterest(Base):
    __tablename__ = "user_interest"

    id = Column(Integer, primary_key=True)
    user_id = Column(String)
    posting_id = Column(Integer, ForeignKey("postings.id"))
    status = Column(String)

class Application(Base):
    __tablename__ = "application"

    id = Column(Integer, primary_key=True)
    user_id = Column(String)
    posting_id = Column(Integer, ForeignKey("postings.id"))
    status = Column(String)
    last_reminder = Column(DateTime)


engine = create_engine("sqlite:///internship_bot.db")
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine, expire_on_commit=False)
