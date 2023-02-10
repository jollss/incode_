import abc
import datetime

import os

from typing import List
import uuid
from collections import namedtuple

import pytz
import requests
from app.database import Base
from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    LargeBinary,
    SmallInteger,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy_utils import IPAddressType, JSONType, UUIDType, ScalarListType

tz = pytz.timezone("America/Mexico_City")


class Session(Base):
    __tablename__ = "sessions"
    id = Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    session_id = Column(String(255), index=True, unique=True)
    user_id = Column(UUIDType(binary=False), index=True)
    token = Column(Text())
    env = Column(String(25))
    url = Column(String(300))
    status = Column(String(50))
    retries = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.now(tz))
    updated_at = Column(DateTime(timezone=True), default=datetime.datetime.now(tz), onupdate=datetime.datetime.now(tz))
    deleted_at = Column(DateTime(timezone=True))
    ocr_result = relationship("OCRResult", backref="session", lazy="dynamic")
    score = relationship("Score", backref="session", uselist=False)


    def __init__(self, session_id = None, user_id = None, token = None, env = None, url = None):
        self.id = uuid.uuid4()
        self.session_id = session_id
        self.user_id = user_id
        self.token = token
        self.env = env
        self.url = url
        self.created_at = datetime.datetime.now(tz)
        self.updated_at = datetime.datetime.now(tz)
        
    def start(self):
        url = f"{os.environ.get('INCODE_URI')}/omni/start/"
        payload = {
            "countryCode": "MX",
            "externalId": self.user_id,
            "redirectionUrl": os.environ.get('REDIRECT_URL'),
            "configurationId": os.environ.get('CONFIGURATION_ID'),
        }
        headers = {
        "api-version": "1.0",
        "x-api-key": os.environ.get('INCODE_API_KEY'),
        "Content-Type": "application/json"
        }
        token = requests.post(url, json=payload, headers=headers)
        print("token",token)
        self.token = token.json()["token"]
        self.env = token.json()["env"]
        print("session_id",token.json()["interviewId"])
        self.session_id = token.json()["interviewId"]
    
    def set_url(self):
        cd_onboarding = os.environ.get('CD_ONBOARDING')
        if cd_onboarding == "true":
            self.url = f"{os.environ.get('CD_ONBOARDING_URI')}/?interviewId={self.session_id}"
        else:
            # self.url = f"https://demo-onboarding.incodesmile.com/curadeuda743/flow/{os.environ.get('CONFIGURATION_ID')}?interviewId={self.session_id}"
            self.url = f"https://saas-onboarding.incodesmile.com/curadeudas444/flow/{os.environ.get('CONFIGURATION_ID')}?interviewId={self.session_id}"
    
    def set_status(self):
        url = f"{os.environ.get('INCODE_URI')}/omni/get/onboarding/status"
        headers = {
            "Content-Type": "application/json",
            "api-version": "1.0",
            "x-api-key": os.environ.get('INCODE_API_KEY'),
            "X-Incode-Hardware-Id": self.token
        }
        self.status = requests.get(url, headers=headers).json()["onboardingStatus"]
        print("token",self.status)
    
    
    def get_ocr_by_token(self)->dict:
        url = f"{os.environ.get('INCODE_URI')}/omni/get/ocr-data/v2"
        headers ={
            "Content-Type": "application/json",
            "api-version": "1.0",
            "x-api-key": os.environ.get('INCODE_API_KEY'),
            "X-Incode-Hardware-Id": self.token
        }
        ocr = requests.get(url, headers=headers).json()
        print("ocr",ocr)
        return ocr['ocrData']

    def get_scores_by_token(self)->dict:
        url = f"{os.environ.get('INCODE_URI')}/omni/get/score"
        headers ={
            "Content-Type": "application/json",
            "api-version": "1.0",
            "x-api-key": os.environ.get('INCODE_API_KEY'),
            "X-Incode-Hardware-Id": self.token
        }
        score = requests.get(url, headers=headers).json()
        print("score",score)
        return score
    
    def get_images(self)->namedtuple:
        images = namedtuple("images", ["front", "back"])
        url = f"{os.environ.get('INCODE_URI')}/omni/get/images"
        headers ={
            "Content-Type": "application/json",
            "api-version": "1.0",
            "x-api-key": os.environ.get('INCODE_API_KEY'),
            "X-Incode-Hardware-Id": self.token
        }
        json = {
            "images": [
                "croppedFrontID",
                "croppedBackID"
            ]
        }
        images_data = requests.post(url,json=json, headers=headers)
        print("images_data",images_data)
        if images_data.status_code == 200:
            images_data = images_data.json()
            return images(images_data["croppedFrontID"], images_data.get("croppedBackID","croppedFrontID"))
        else:
            return images(None, None)
        
    def increment_retries(self):
        retries = 0
        if self.retries is None:
            self.retries = retries
        else:
            self.retries = self.retries + 1
        
        


class OCRResult(Base):
    __tablename__ = "ocr_results"
    id = Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUIDType(binary=False), ForeignKey("sessions.id"))
    full_name = Column(String(255))
    first_name = Column(String(255))
    paternal_name = Column(String(255))
    maternal_name = Column(String(255))
    name = Column(JSONType)
    address = Column(Text)
    address_fields = Column(JSONType)
    full_address = Column(Boolean)
    invalid_address = Column(Boolean)
    checked_address = Column(Text)
    checked_address_bean = Column(JSONType)
    exterior_number = Column(String(255))
    type_of_id = Column(String(255))
    document_front_subtype = Column(String(255))
    document_back_subtype = Column(String(255))
    birth_date = Column(Integer)
    gender = Column(String(25))
    clave_de_elector = Column(String(255))
    curp = Column(String(20))
    numero_emision_credencial = Column(String(255))
    cic = Column(String(255))
    ocr = Column(String(255))
    expire_at = Column(String(255))
    expiration_date = Column(Integer)
    issue_date = Column(Integer)
    registration_date = Column(Integer)
    issuing_country = Column(String(255))
    nationality = Column(String(255))
    nationality_mrz = Column(String(255))
    not_extracted = Column(String(255))
    not_extracted_details = Column(ScalarListType())
    mrz_1 = Column(String(255))
    mrz_2 = Column(String(255))
    mrz_3 = Column(String(255))
    full_name_mrz = Column(String(255))
    documentNumberCheckDigit = Column(String(10))
    dateOfBirthCheckDigit = Column(String(10))
    expirationDateCheckDigit = Column(String(10))
    ocrDataConfidence = Column(JSONType)
    created_at = Column(DateTime, nullable=True, default=datetime.datetime.now(tz=tz))
    updated_at = Column(DateTime, nullable=True, default=datetime.datetime.now(tz=tz))
    
    def __init__(self, session_id, **kwargs):
        self.id == uuid.uuid4()
        self.session_id = session_id
        self.full_name = kwargs.get("fullName")
        self.first_name = kwargs.get("firstName")
        self.paternal_name = kwargs.get("paternalName")
        self.maternal_name = kwargs.get("maternalName")
        self.name = kwargs.get("name")
        self.address = kwargs.get("address")
        self.address_fields = kwargs.get("addressFields")
        self.full_address = kwargs.get("fullAddress")
        self.invalid_address = kwargs.get("invalidAddress")
        self.checked_address = kwargs.get("checkedAddress")
        self.checked_address_bean = kwargs.get("checkedAddressBean")
        self.exterior_number = kwargs.get("exteriorNumber")
        self.type_of_id = kwargs.get("typeOfId")
        self.document_front_subtype = kwargs.get("documentFrontSubtype")
        self.document_back_subtype = kwargs.get("documentBackSubtype")
        self.birth_date = kwargs.get("birthDate")
        self.gender = kwargs.get("gender")
        self.clave_de_elector = kwargs.get("claveDeElector")
        self.curp = kwargs.get("curp")
        self.numero_emision_credencial = kwargs.get("numeroEmisionCredencial")
        self.cic = kwargs.get("cic")
        self.ocr = kwargs.get("ocr")
        self.expire_at = kwargs.get("expireAt")
        self.expiration_date = kwargs.get("expirationDate")
        self.issue_date = kwargs.get("issueDate")
        self.registration_date = kwargs.get("registrationDate")
        self.issuing_country = kwargs.get("issuingCountry")
        self.nationality = kwargs.get("nationality")
        self.nationality_mrz = kwargs.get("nationalityMrz")
        self.not_extracted = kwargs.get("notExtracted")
        self.not_extracted_details = kwargs.get("notExtractedDetails")
        self.mrz_1 = kwargs.get("mrz1")
        self.mrz_2 = kwargs.get("mrz2")
        self.mrz_3 = kwargs.get("mrz3")
        self.full_name_mrz = kwargs.get("fullNameMrz")
        self.documentNumberCheckDigit = kwargs.get("documentNumberCheckDigit")
        self.dateOfBirthCheckDigit = kwargs.get("dateOfBirthCheckDigit")
        self.expirationDateCheckDigit = kwargs.get("expirationDateCheckDigit")
        self.ocrDataConfidence = kwargs.get("ocrDataConfidence")
        self.created_at = datetime.datetime.now(tz=tz)
        self.updated_at = datetime.datetime.now(tz=tz)
        


class Score(Base):
    __tablename__ = "scores"
    id = Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUIDType(binary=False), ForeignKey("sessions.id"))
    id_validation_id = Column(UUIDType(binary=False), ForeignKey("id_validations.id"), index=True)
    curp_verification_id = Column(UUIDType(binary=False), ForeignKey("curp_verifications.id"), index=True)
    id_ocr_confidence_id = Column(UUIDType(binary=False), ForeignKey("id_ocr_confidences.id"), index=True)
    retry_info = Column(JSONType)
    overall_value = Column(String(10))
    overall_status = Column(String(30))
    created_at = Column(DateTime, nullable=True, default=datetime.datetime.now(tz=tz))
    updated_at = Column(DateTime, nullable=True, default=datetime.datetime.now(tz=tz))
    id_validation = relationship("IdValidation", backref="score", uselist=False)
    curp_verification = relationship("CurpVerification", backref="score", uselist=False)
    id_ocr_confidence = relationship("IdOcrConfidence", backref="score", uselist=False)
    
    def __init__(self, session_id, **kwargs):
        self.id == uuid.uuid4()
        self.session_id = session_id
        self.id_validation_id = kwargs.get("id_validation")
        self.curp_verification_id = kwargs.get("curp_verification")
        self.id_ocr_confidence_id = kwargs.get("id_ocr_confidence")
        self.retry_info = kwargs.get("retryInfo")
        self.overall_value = kwargs.get("value")
        self.overall_status = kwargs.get("status")
        self.created_at = datetime.datetime.now(tz=tz)
        self.updated_at = datetime.datetime.now(tz=tz)


class OverallBase(abc.ABC):
    value : str
    status : str
    key : str



class IdValidation(Base):
    __tablename__ = "id_validations"
    id = Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    photo_security_and_quality:List[OverallBase] = Column(JSONType)
    id_specific:List[OverallBase] = Column(JSONType)
    overall_value:str = Column(String(10))
    overall_status:str = Column(String(30))
    
    def __init__(self, **kwargs):
        self.id == uuid.uuid4()
        self.photo_security_and_quality = kwargs.get("photoSecurityAndQuality")
        self.id_specific = kwargs.get("idSpecific")
        self.overall_value = kwargs.get("overall").get("value")
        self.overall_status = kwargs.get("overall").get("status")
        self.created_at = datetime.datetime.now(tz=tz)
        self.updated_at = datetime.datetime.now(tz=tz)


class CurpVerification(Base):
    __tablename__ = "curp_verifications"
    id = Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    success:bool = Column(Boolean)
    curp:str = Column(String(255))
    sex:str = Column(String(30))
    nationality :str = Column(String(30))
    result:str = Column(String(255))
    renapo_valid:bool = Column(Boolean)
    name : str = Column(String(255))
    paternal_surname :str = Column(String(255))
    mothers_maiden_name:str = Column(String(255))
    birthdate = Column(Date)
    entity_birth:str = Column(String(10))
    probation_document:str = Column(String(5))
    probation_document_data = Column(JSONType)
    status_curp = Column(String(10))
    
    def __init__(self, **kwargs):
        self.id == uuid.uuid4()
        self.success = kwargs.get("success")
        self.curp = kwargs.get("curp")
        self.sex = kwargs.get("sex")
        self.nationality = kwargs.get("nationality")
        self.result = kwargs.get("result")
        self.renapo_valid = kwargs.get("renapo_valid")
        self.name = kwargs.get("names")
        self.paternal_surname = kwargs.get("paternal_surname")
        self.mothers_maiden_name = kwargs.get("mothers_maiden_name")
        self.birthdate = kwargs.get("birthdate")
        self.entity_birth = kwargs.get("entity_birth")
        self.probation_document = kwargs.get("probation_document")
        self.probation_document_data = kwargs.get("probation_document_data")
        self.status_curp = kwargs.get("status_curp")

class IdOcrConfidence(Base):
    __tablename__ = "id_ocr_confidences"
    id = Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    overall_value:str = Column(String(10))
    overall_status:str = Column(String(30))


    def __init__(self, **kwargs):
        self.id == uuid.uuid4()
        self.overall_value = kwargs.get("overallConfidence").get("value")
        self.overall_status = kwargs.get("overallConfidence").get("status")