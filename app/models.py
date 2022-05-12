import enum
import json
from struct import unpack
import uuid
import hashlib
import datetime
import pytz
import random
import string
import unidecode
from collections import namedtuple
from sqlalchemy import Column, String, Text, DateTime, Date, ForeignKey, Boolean, Enum, Integer, BigInteger, SmallInteger,LargeBinary, Float
from sqlalchemy.orm import relationship
from sqlalchemy.orm.exc import NoResultFound 
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import UUIDType, JSONType, IPAddressType
from dateutil.parser import parse

from app.database import Base, db_session

tz = pytz.timezone('America/Mexico_City')

class ResultsIne(Base):
    __tablename__ = 'results_ine'
    id = Column(Integer, primary_key=True)
    user_id = Column(UUIDType(binary=False), unique=True)
    sub_nombre_economica = Column(String(255))
    sub_clave_economica_id = Column(String(20))
    email_user = Column(String(255))
    front = Column(String(255))
    back = Column(String(255))
    mensaje_error = Column(String(255))
    rid_solicitud = Column(BigInteger, nullable=True)
    status_ine_loads = Column(Integer)#0-no ha cargado imagnes/1-cargo imagenes a QB/2-cargo imagenes-spearow-F/3-cargo imagenes-spearow-B/4-cargo actividad/9-sin datos para enviar
    #ruta_all = Column(String(255))
    created_at = Column(DateTime, nullable=True,default=datetime.datetime.now(tz=tz))  

    def __init__(self, user_id,email_user,rid_solicitud):
        self.user_id = user_id
        self.email_user = email_user
        self.rid_solicitud = rid_solicitud
        self.created_at = datetime.datetime.now(tz=tz)
        

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


class HookLog(Base):
    __tablename__ = 'hook_logs'
    id = Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    event_type = Column(String(255))
    event_action = Column(String(255))
    object = Column(JSONType)
    version = Column(Float)
    timestamp = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=True,default=datetime.datetime.now(tz=tz))
    updated_at = Column(DateTime, nullable=True,default=datetime.datetime.now(tz=tz))
    
    def __init__(self, event_type, event_action, object, version, timestamp):
        self.event_type = event_type
        self.event_action = event_action
        self.object = object
        self.version = version
        self.timestamp = timestamp
        self.created_at = datetime.datetime.now(tz=tz)
        self.updated_at = datetime.datetime.now(tz=tz)
    
    def get_ids(self):
        ids = namedtuple('ids', 'create update process_id account_id validation_id check_id')
        if self.event_action == 'created':
            print('created')
            if self.event_type == 'document_validation':
                return ids(False, True, self.object['identity_process_id'], None, self.object['validation_id'], None)
            if self.event_type == 'identity_process':
                print('identity_process')
                return ids(True, False, self.object['process_id'], self.object['account_id'], None, None)
        if self.event_action == 'succeeded':
            if self.event_type == 'document_validation':
                return ids(False, False, self.object['identity_process_id'], None, None,self.object['details']['background_check']['check_id'])
        
    def get_validation_id(self):
        if self.event_type == 'document_validation':
            if self.event_action == 'succeeded' or self.event_action == 'failed':
                return self.object['validation_id']
            
    def get_check_id(self):
        if self.event_type == 'document_validation':
            if self.event_action == 'succeeded':
                return self.object['details']['background_check']['check_id']


class ProcessID(Base):
    __tablename__ = 'process_ids'
    id = Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    proccess_id = Column(String(255), index=True)
    account_id = Column(String(255), index=True)
    first_check_id = Column(String(255), index=True)
    last_check_id = Column(String(255), index=True)
    validation_id = Column(String(255), index=True)
    user_id = Column(UUIDType(binary=False))
    created_at = Column(DateTime, nullable=True,default=datetime.datetime.now(tz=tz))
    updated_at = Column(DateTime, nullable=True,default=datetime.datetime.now(tz=tz))
    
    def __init__(self,**kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                if value is not None:
                    setattr(self, key, value)
        self.created_at = datetime.datetime.now(tz=tz)
        self.updated_at = datetime.datetime.now(tz=tz)
    
    
    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                if value is not None:
                    setattr(self, key, value)
                    self.updated_at = datetime.datetime.now(tz=tz)
        

class DigitalId(Base):
    __tablename__ = 'digital_ids'
    id = Column(String(255), primary_key=True)
    status = Column(String(255))
    creation_date = Column(DateTime, nullable=True)
    update_date = Column(DateTime)
    
    def __init__(self, proccess_id, status, creation_date, update_date):
        self.proccess_id = proccess_id
        self.status = status
        self.creation_date = creation_date
        self.update_date = update_date


class Validation(Base):
    __tablename__ = 'validations'
    id = Column(String(255), primary_key=True)
    ip_address = Column(IPAddressType, nullable=True)
    type = Column(String(255), nullable=True)
    validation_status = Column(String(255), nullable=True)
    creation_date = Column(DateTime, nullable=True)
    declined_reason = Column(String(255), nullable=True)
    failure_reason = Column(String(255), nullable=True)
    # validation_detail = Column(UUIDType(binary=False), ForeignKey('validation_details.id'))
    # validation_document = Column(UUIDType(binary=False), ForeignKey('validation_documents.id'))
    attachment_status = Column(String(255), nullable=True)
    retry_of_id = Column(String(255))
    
    def __init__(self, **kwargs):
        if 'validation_id' in kwargs:
            self.id = kwargs['validation_id']
        for key, value in kwargs.items():
            if hasattr(self, key):
                if value is not None:
                    if 'creation_date' in key:
                        # value = datetime.datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.Z')
                        value = parse(value, ignoretz=True)
                        # value = datetime.datetime.fromisoformat(value)
                    setattr(self, key, value)


class ValidationDetail(Base):
    __tablename__ = 'validation_details'
    id = Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    validation_id = Column(String(255), ForeignKey('validations.id'))
    country = Column(String(255))
    creation_date = Column(DateTime)
    date_of_birth = Column(Date)
    document_number = Column(String(255))
    document_type = Column(String(255))
    expiration_date = Column(DateTime)
    gender = Column(String(255))
    issue_date = Column(DateTime)
    last_name = Column(String(255))
    machine_readable = Column(String(255))
    municipality = Column(Integer)
    municipality_name = Column(String(255))
    state = Column(Integer)
    state_name = Column(String(255))
    locality = Column(Integer)
    section = Column(Integer)
    elector_key = Column(String(255))
    ocr = Column(String(255))
    cic = Column(String(255))
    citizen_id = Column(String(255))
    name = Column(String(255))
    registration_date = Column(DateTime)
    residence_address = Column(String(255))
    update_date = Column(DateTime)
    front_url = Column(String(255))
    back_url = Column(String(255))
    
    def __init__(self,validation_id=None, **kwargs):
        self.validation_id = validation_id
        if 'mexico_document' in kwargs:
            kwargs.update(**kwargs['mexico_document'])
        print(json.dumps(kwargs, indent=4))
        for key, value in kwargs.items():
            if hasattr(self, key):
                if value is not None:
                    if 'date' in key:
                        value = parse(value, ignoretz=True)
                    setattr(self, key, value)


class ValidationDocument(Base):
    __tablename__ = 'validation_documents'
    id = Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    validation_id = Column(String(255), ForeignKey('validations.id'))
    validation_name = Column(String(255))
    result = Column(String(255))
    validation_type = Column(String(255))
    message = Column(String(255))
    manually_reviewed = Column(Boolean)
    
    def __init__(self,validation_id=None, **kwargs):
        self.validation_id = validation_id
        for key, value in kwargs.items():
            if hasattr(self, key):
                if value is not None:
                    setattr(self, key, value)

class Check(Base):
    __tablename__ = 'checks'
    id = Column(String(255), primary_key=True)
    cic = Column(String(255))
    citizen_id = Column(String(255))
    company_summary = Column(JSONType)
    country = Column(String(255))
    creation_date = Column(DateTime)
    date_of_birth = Column(Date)
    document_recognition_id = Column(String(255))
    elector_key = Column(String(255))
    expedition_date = Column(DateTime)
    issue_date = Column(DateTime)
    first_name = Column(String(255))
    name_score = Column(Integer)
    id_score = Column(Integer)
    last_name = Column(String(255))
    ocr = Column(String(255))
    score = Column(Integer)
    scores = Column(JSONType)
    status = Column(String(255))
    statuses = Column(JSONType)
    summary = Column(JSONType)
    update_date = Column(DateTime)
    vehicle_summary = Column(JSONType)
    national_id = Column(String(255))
    owner_document_type = Column(String(255))
    type = Column(String(255))
    
    def __init__(self,**kwargs):
        if 'check_id' in kwargs:
            self.id = kwargs['check_id']
        for key, value in kwargs.items():
            if hasattr(self, key):
                if value is not None:
                    if 'date' in key:
                        value = parse(value, ignoretz=True)
                    setattr(self, key, value)