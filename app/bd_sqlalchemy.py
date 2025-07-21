import os
from sqlalchemy import create_engine, Column, Integer, String, Date, Numeric
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

Base = declarative_base()

class Movimiento(Base):
    __tablename__ = 'movimientos'
    id     = Column(Integer, primary_key=True)
    fecha  = Column(Date)
    monto  = Column(Numeric(12, 2))
    cuenta = Column(String)

db_user = os.getenv("POSTGRES_USER", "finanuser")
db_pass = os.getenv("POSTGRES_PASSWORD", "finanpass")
db_name = os.getenv("POSTGRES_DB", "finandb")
db_host = os.getenv("POSTGRES_HOST", "db")        # ← nombre del servicio docker
engine   = create_engine(f"postgresql://{db_user}:{db_pass}@{db_host}/{db_name}")

Session = sessionmaker(bind=engine)
Base.metadata.create_all(engine)

def save_record(fields):
    session = Session()
    mov = Movimiento(
        fecha=datetime.strptime(fields['fecha'], '%d/%m/%Y'),
        monto=float(fields['monto']),
        cuenta=fields['cuenta']
    )
    session.add(mov)
    session.commit()
    session.close()