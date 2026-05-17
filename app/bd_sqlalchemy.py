import os
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    BigInteger,
    String,
    Date,
    DateTime,
    Numeric,
    Boolean,
    ForeignKey,
    text,
    func,
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime

Base = declarative_base()


class Usuario(Base):
    __tablename__ = 'usuarios'

    id = Column(Integer, primary_key=True)
    telegram_user_id = Column(BigInteger, unique=True, nullable=False)
    telegram_username = Column(String(255))
    first_name = Column(String(255))
    last_name = Column(String(255))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


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
    usuario_id = Column(Integer, ForeignKey('usuarios.id'), nullable=True)

    tipo = relationship('TipoMovimiento')
    entidad = relationship('Entidad')
    usuario = relationship('Usuario')


db_user = os.getenv("POSTGRES_USER", "finanuser")
db_pass = os.getenv("POSTGRES_PASSWORD", "finanpass")
db_name = os.getenv("POSTGRES_DB", "finandb")
db_host = os.getenv("POSTGRES_HOST", "db")
engine = create_engine(f"postgresql://{db_user}:{db_pass}@{db_host}/{db_name}")

Session = sessionmaker(bind=engine)
Base.metadata.create_all(engine)


def _ensure_schema():
    """Add new columns if the existing table is outdated."""
    columns = {
        "hora": "VARCHAR(10)",
        "nro_comprobante": "VARCHAR(50)",
        "cuenta_origen": "VARCHAR(50)",
        "beneficiario": "VARCHAR(120)",
        "es_ingreso": "BOOLEAN",
        "tipo_id": "INTEGER",
        "entidad_id": "INTEGER",
        "usuario_id": "INTEGER",
    }

    with engine.begin() as conn:
        result = conn.execute(
            text("SELECT column_name FROM information_schema.columns WHERE table_name='movimientos'")
        )
        existing = {row[0] for row in result}

        for name, coltype in columns.items():
            if name not in existing:
                conn.execute(text(f"ALTER TABLE movimientos ADD COLUMN {name} {coltype}"))

        # Ensure usuarios table exists and FK is in place
        result = conn.execute(
            text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name='usuarios')")
        )
        if not result.scalar():
            conn.execute(text("""
                CREATE TABLE usuarios (
                    id SERIAL PRIMARY KEY,
                    telegram_user_id BIGINT UNIQUE NOT NULL,
                    telegram_username VARCHAR(255),
                    first_name VARCHAR(255),
                    last_name VARCHAR(255),
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            """))

        # Add FK if missing
        result = conn.execute(
            text("""
                SELECT 1 FROM information_schema.table_constraints
                WHERE constraint_name = 'fk_movimientos_usuario'
                  AND table_name = 'movimientos'
            """)
        )
        if not result.scalar():
            conn.execute(text("""
                ALTER TABLE movimientos
                ADD CONSTRAINT fk_movimientos_usuario
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
                ON DELETE SET NULL ON UPDATE CASCADE
            """))


_ensure_schema()


def _get_or_create(session, model, **kwargs):
    inst = session.query(model).filter_by(**kwargs).first()
    if inst:
        return inst
    inst = model(**kwargs)
    session.add(inst)
    session.flush()
    return inst


def get_or_create_user(telegram_user_id, telegram_username=None, first_name=None, last_name=None):
    session = Session()
    try:
        user = session.query(Usuario).filter_by(telegram_user_id=telegram_user_id).first()
        if user:
            changed = False
            if telegram_username is not None and user.telegram_username != telegram_username:
                user.telegram_username = telegram_username
                changed = True
            if first_name is not None and user.first_name != first_name:
                user.first_name = first_name
                changed = True
            if last_name is not None and user.last_name != last_name:
                user.last_name = last_name
                changed = True
            if changed:
                user.updated_at = datetime.now()
                session.commit()
                print(f"👤 Usuario actualizado: {telegram_user_id} ({telegram_username})")
            else:
                print(f"👤 Usuario ya existente: {telegram_user_id} ({telegram_username})")
        else:
            user = Usuario(
                telegram_user_id=telegram_user_id,
                telegram_username=telegram_username,
                first_name=first_name,
                last_name=last_name,
            )
            session.add(user)
            session.commit()
            print(f"👤 Usuario creado: {telegram_user_id} ({telegram_username})")
        return user.id
    finally:
        session.close()


def save_record(fields, usuario_id=None):
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
            usuario_id=usuario_id,
        )
        session.add(mov)
        session.commit()
        print(f"✅ Movimiento insertado (usuario_id={usuario_id}): {mov.fecha} - {mov.monto}")
    finally:
        session.close()
