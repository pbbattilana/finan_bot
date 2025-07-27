import os
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Date,
    Numeric,
    Boolean,
    ForeignKey,
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime

Base = declarative_base()


class Entidad(Base):
    __tablename__ = 'entidades'
    id = Column(Integer, primary_key=True)
    nombre = Column(String, unique=True)


class TipoMovimiento(Base):
    __tablename__ = 'tipos_movimiento'
    id = Column(Integer, primary_key=True)
    nombre = Column(String, unique=True)


class Movimiento(Base):
    __tablename__ = 'movimientos'

    id = Column(Integer, primary_key=True)
    fecha = Column(Date)
    hora = Column(String)
    monto = Column(Numeric(12, 2))
    nro_comprobante = Column(String)
    cuenta_origen = Column(String)
    beneficiario = Column(String)
    es_ingreso = Column(Boolean, default=False)

    tipo_id = Column(Integer, ForeignKey('tipos_movimiento.id'))
    entidad_id = Column(Integer, ForeignKey('entidades.id'))

    tipo = relationship('TipoMovimiento')
    entidad = relationship('Entidad')

db_user = os.getenv("POSTGRES_USER", "finanuser")
db_pass = os.getenv("POSTGRES_PASSWORD", "finanpass")
db_name = os.getenv("POSTGRES_DB", "finandb")
db_host = os.getenv("POSTGRES_HOST", "db")        # ← nombre del servicio docker
engine   = create_engine(f"postgresql://{db_user}:{db_pass}@{db_host}/{db_name}")

Session = sessionmaker(bind=engine)
Base.metadata.create_all(engine)

def _get_or_create(session, model, **kwargs):
    inst = session.query(model).filter_by(**kwargs).first()
    if inst:
        return inst
    inst = model(**kwargs)
    session.add(inst)
    session.flush()
    return inst


def save_record(fields):
    session = Session()
    try:
        tipo_name = fields.get('tipo', 'desconocido')
        tipo = _get_or_create(session, TipoMovimiento, nombre=tipo_name)

        entidad = None
        if fields.get('entidad'):
            entidad = _get_or_create(session, Entidad, nombre=fields['entidad'])

        fecha_val = fields.get('fecha')
        if fecha_val:
            if '-' in fecha_val:
                fecha_obj = datetime.strptime(fecha_val, '%Y-%m-%d')
            else:
                fecha_obj = datetime.strptime(fecha_val, '%d/%m/%Y')
        else:
            fecha_obj = None

        mov = Movimiento(
            fecha=fecha_obj,
            hora=fields.get('hora'),
            monto=float(fields['monto']),
            nro_comprobante=fields.get('nro_comprobante'),
            cuenta_origen=fields.get('cuenta_origen') or fields.get('cuenta'),
            beneficiario=fields.get('beneficiario') or fields.get('comercio'),
            es_ingreso=fields.get('ingreso', False),
            tipo=tipo,
            entidad=entidad,
        )
        session.add(mov)
        session.commit()
    finally:
        session.close()