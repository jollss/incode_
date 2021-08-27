import enum
import uuid
import hashlib
import datetime
import pytz
import random
import string
import unidecode

from sqlalchemy import Column, String, Text, DateTime, Date, ForeignKey, Boolean, Enum, Integer, BigInteger, SmallInteger,LargeBinary
from sqlalchemy.orm import relationship
from sqlalchemy.orm.exc import NoResultFound 
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import UUIDType

from app.database import Base, db_session

tz = pytz.timezone('America/Mexico_City')

class ResultsIne(Base):
    __tablename__ = 'results_ine'
    id = Column(Integer, primary_key=True)
    user_id = Column(UUIDType(binary=False), unique=True)
    sub_nombre_economica = Column(String(255))
    sub_clave_economica_id = Column(String(20))
    email_user = Column(String(255))
    #front = Column(String(255))
    #back = Column(String(255))
    mensaje_error = Column(String(255))
    rid_solicitud = Column(BigInteger, nullable=True)
    status_ine_loads = Column(Integer)#0-no ha cargado imagnes/1-cargo imagenes a QB/2-cargo imagenes-spearow-F/3-cargo imagenes-spearow-B/4-cargo actividad/9-sin datos para enviar
    #ruta_all = Column(String(255))
    created_at = Column(DateTime, nullable=True,default=datetime.datetime.now(tz=tz))  

    def __init__(self, user_id,email_user,status_ine_loads,mensaje_error,rid_solicitud):
        self.user_id = user_id
        self.email_user = email_user
        self.status_ine_loads = status_ine_loads
        self.mensaje_error = mensaje_error
        self.rid_solicitud = rid_solicitud
        
        

    def __repr__(self):
        return '%r' % (self.id)

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                if value is not None:
                    setattr(self, key, value)

class actividad_economica(Base):
    __tablename__ = 'actividad_economica'
    id = Column(Integer, primary_key=True)
    clave_economica = Column(String(20))
    created_at = Column(DateTime, nullable=True,default=datetime.datetime.now(tz=tz))

    def __init__(self, clave_economica):
        self.clave_economica = clave_economica

    def __repr__(self):
        return '%r' % (self.id)

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                if value is not None:
                    setattr(self, key, value)

class actividad_economicaCat(Base):
    __tablename__ = 'cat_actividad_economica'
    id = Column(Integer, primary_key=True)
    cat_nombre_economica = Column(String(100))
    cat_actividad_economica_id = Column(Integer, ForeignKey('actividad_economica.id'))
    created_at = Column(DateTime, nullable=True,default=datetime.datetime.now(tz=tz))

    def __init__(self, cat_nombre_economica, cat_actividad_economica_id):
        self.cat_nombre_economica = cat_nombre_economica
        self.cat_actividad_economica_id = cat_actividad_economica_id

    def __repr__(self):
        return '%r' % (self.id)

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                if value is not None:
                    setattr(self, key, value)

class actividad_economica_sub_cat(Base):
    __tablename__ = 'sub_cat_actividad_economica'
    id = Column(Integer, primary_key=True)
    sub_nombre_economica = Column(String(255))
    sub_clave_economica_id = Column(String(20))
    sub_cat_actividad_economica_id = Column(Integer, ForeignKey('cat_actividad_economica.id'))
    created_at = Column(DateTime, nullable=True,default=datetime.datetime.now(tz=tz))

    def __init__(self, sub_nombre_economica, sub_clave_economica_id,sub_cat_actividad_economica_id):
        self.sub_nombre_economica = sub_nombre_economica
        self.sub_clave_economica_id = sub_clave_economica_id
        self.sub_cat_actividad_economica_id = sub_cat_actividad_economica_id

    def __repr__(self):
        return '%r' % (self.id)

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                if value is not None:
                    setattr(self, key, value)
