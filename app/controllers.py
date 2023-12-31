# import logging
import os

# import pytz
import sys
from io import BytesIO
from os import path

# import string
import requests

# import base64
from flask import jsonify, render_template
from sentry_sdk import capture_exception, capture_message

from app.tasks import celery

# from weasyprint import HTML
# from sqlalchemy.sql.expression import false
sys.path = ["", ".."] + sys.path[1:]
# from flask import Flask, request
import base64
import datetime
import traceback
from base64 import b64encode

from dateutil.parser import parse
from PIL import Image

# from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

# import calendar
# from json.decoder import JSONDecodeError
# import time
from app.database import db_session
from app.models import *

# import io
# from os import remove


def datos_mewtwo(datos):
    try:
        e = db_session.query(ResultsIne).filter_by(user_id=datos["user"]).first()
        if e == None:
            a = ResultsIne(
                user_id=datos["user"],
                email_user=datos["correo"],
                rid_solicitud=datos["rid_solicitud"],
                # status_ine_loads=1,
            )
            db_session.add(a)
            db_session.commit()
            db_session.close()
        else:
            e.email_user = datos["correo"]
            e.rid_solicitud = datos["rid_solicitud"]
            # e.status_ine_loads = 1
            db_session.add(e)
            db_session.commit()
            db_session.close()
        SPEAROW_URI = os.environ.get("SPEAROW_URI")
        headers = {"Content-Type": "application/json"}
        data = {
            "user_id": datos["user"],
            "back_image": datos["back"],
            "front_image": datos["frente"],
        }
        r = requests.post(SPEAROW_URI + "/api/v1/file/img", json=data, headers=headers)
        spearoowcodeF = r.status_code
        if spearoowcodeF == 200:
            json_data = r.json()
            r = send_abra(json_data)
            if r == True:
                return True
            else:
                return False
        else:
            return False
    except Exception as e:
        capture_exception(e)
        traceback.print_exc()


def send_abra(data):
    l = db_session.query(ResultsIne).filter_by(user_id=data["message"]).first()
    try:
        ABRA_URI = os.environ.get("ABRA_URI")
        if "imageF" in data["response"]:
            headers = {"Content-Type": "application/json"}
            body = {"url": data["response"]["imageF"]}
            g = requests.post(ABRA_URI + "/api/v1/url", json=body, headers=headers)
            abracode = g.status_code
            if abracode == 200:
                gjson_data = g.json()
                l.front = gjson_data["url"]

        if "imageB" in data["response"]:
            headers = {"Content-Type": "application/json"}
            body = {"url": data["response"]["imageB"]}
            g = requests.post(ABRA_URI + "/api/v1/url", json=body, headers=headers)
            abracode = g.status_code
            if abracode == 200:
                gjson_data = g.json()
                l.back = gjson_data["url"]
        l.status_ine_loads = 2
        db_session.add(l)
        db_session.commit()
        return True
    except Exception as e:
        capture_exception(e)
        return False


def send_qbF(frente="", user="", correo="", rid=""):
    tam_frente = len(frente)
    d = datetime.datetime.now(tz=tz).strftime("%Y%m%d")
    carpeta = "app/ineImages/"
    if tam_frente > 0:
        n = str(user)
        if frente:
            ext = "jpeg"
            if frente.find("/png;") > 0:
                ext = "png"
            if frente.find("/jpg;") > 0:
                ext = "jpg"
            if frente.find("/gif;") > 0:
                ext = "gif"
            if frente.find("/heic;") > 0:
                ext = "heic"
            imagenF = frente
            imgf = imagenF.replace("data:image/jpeg;base64,", "")
            imgf = imgf.replace("data:image/png;base64,", "")
            imgf = imgf.replace("data:image/jpg;base64,", "")
            imgf = imgf.replace("data:image/gif;base64,", "")
            imgf = imgf.replace("data:image/heic;base64,", "")
            FLASK_ENV = os.environ.get("FLASK_ENV")
            if FLASK_ENV == "production":

                datafrente = {
                    "to": "bgrm6tt7q",
                    "data": [
                        {  #'281':{'value':{'fileName':f"atras {result_ine.rid_solicitud}.jpeg" ,'data':back}},
                            "79": {
                                "value": {
                                    "fileName": f"frente {rid}.{ext}",
                                    "data": imgf,
                                }
                            },
                            "3": {"value": rid},
                        }
                    ],
                }
                USERTOKEN = os.environ.get("USERTOKEN")
                QBR = os.environ.get("QBRealmHostname")
                UserAgent = os.environ.get("UserAgent")

                headers = {
                    "QB-Realm-Hostname": QBR,
                    "User-Agent": UserAgent,
                    "Authorization": "QB-USER-TOKEN {}".format(USERTOKEN),
                    "Content-Type": "application/json",
                }

                QBINeF = requests.post(
                    "https://api.quickbase.com/v1/records",
                    json=datafrente,
                    headers=headers,
                )
                codeF = QBINeF.status_code
            else:
                codeF = 200
                rid = 123
            us = db_session.query(ResultsIne).filter_by(user_id=user).first()
            if codeF == 200:
                if us is None:
                    a = ResultsIne(
                        user_id=user,
                        email_user=correo,
                        mensaje_error="se cargaron imagenes a QB",
                        rid_solicitud=rid,
                        status_ine_loads=1,
                    )
                    db_session.add(a)
                    db_session.commit()
                else:
                    us.mensaje_error = "se cargaron imagenes a QB"
                    us.status_ine_loads = 1
                    db_session.add(us)
                    db_session.commit()
                db_session.close()
                data_sperow = {
                    "correo": correo,
                    "rid": rid,
                    "status": True,
                    "front_image": frente,
                    "user": user,
                }
                respuesta_spearow = send_sperow(data_sperow)
                e = db_session.query(ResultsIne).filter_by(user_id=user).first()
                if respuesta_spearow == True:
                    e.status_ine_loads = 2
                    e.mensaje_error = "Se cargo imagen a DB F"
                    db_session.add(e)
                    db_session.commit()
                    db_session.close()
                    return True
                else:
                    e.status_ine_loads = 4
                    e.mensaje_error = "No se cargo a DB"
                    db_session.add(e)
                    db_session.commit()
                    db_session.close()
                    return False
            else:
                if us is None:
                    a = ResultsIne(
                        user_id=user,
                        email_user=correo,
                        mensaje_error="no se cargaron imagenes a QB",
                        rid_solicitud=rid,
                        status_ine_loads=1,
                    )
                    db_session.add(a)
                    db_session.commit()
                else:
                    us.mensaje_error = "no se cargaron imagenes a QB"
                    us.status_ine_loads = 0
                    db_session.add(us)
                    db_session.commit()
                db_session.close()
                return False

    else:
        return False


def send_qbB(atras="", user="", correo="", rid=""):
    tam_atras = len(atras)
    d = datetime.datetime.now(tz=tz).strftime("%Y%m%d")
    carpeta = "app/ineImages/"
    if tam_atras > 0:
        n = str(user)
        if atras:
            ext = "jpeg"
            if atras.find("/png;") > 0:
                ext = "png"
            if atras.find("/jpg;") > 0:
                ext = "jpg"
            if atras.find("/gif;") > 0:
                ext = "gif"
            if atras.find("/heic;") > 0:
                ext = "heic"
            imagenB = atras
            imgb = imagenB.replace("data:image/jpeg;base64,", "")
            imgb = imgb.replace("data:image/png;base64,", "")
            imgb = imgb.replace("data:image/jpg;base64,", "")
            imgb = imgb.replace("data:image/gif;base64,", "")
            imgb = imgb.replace("data:image/heic;base64,", "")
            FLASK_ENV = os.environ.get("FLASK_ENV")
            if FLASK_ENV == "production":
                datafrente = {
                    "to": "bgrm6tt7q",
                    "data": [
                        {  #'79':{'value':{'fileName':f"atras {result_ine.rid_solicitud}.jpeg" ,'data':back}},
                            "281": {
                                "value": {
                                    "fileName": f"atras {rid}.{ext}",
                                    "data": imgb,
                                }
                            },
                            "3": {"value": rid},
                        }
                    ],
                }
                USERTOKEN = os.environ.get("USERTOKEN")
                QBR = os.environ.get("QBRealmHostname")
                UserAgent = os.environ.get("UserAgent")

                headers = {
                    "QB-Realm-Hostname": QBR,
                    "User-Agent": UserAgent,
                    "Authorization": "QB-USER-TOKEN {}".format(USERTOKEN),
                    "Content-Type": "application/json",
                }
                QBINeF = requests.post(
                    "https://api.quickbase.com/v1/records",
                    json=datafrente,
                    headers=headers,
                )
                codeF = QBINeF.status_code
            else:
                codeF = 200
                rid = 123
            us = db_session.query(ResultsIne).filter_by(user_id=user).first()
            if codeF == 200:
                if us is None:
                    a = ResultsIne(
                        user_id=user,
                        email_user=correo,
                        mensaje_error="se cargaron imagenes a QB",
                        rid_solicitud=rid,
                        status_ine_loads=1,
                    )
                    db_session.add(a)
                    db_session.commit()
                else:
                    us.mensaje_error = "se cargaron imagenes a QB"
                    us.status_ine_loads = 1
                    db_session.add(us)
                    db_session.commit()
                db_session.close()
                data_sperow = {
                    "correo": correo,
                    "rid": rid,
                    "status": True,
                    "back_image": atras,
                    "user": user,
                }
                respuesta_spearow = send_sperow(data_sperow)
                e = db_session.query(ResultsIne).filter_by(user_id=user).first()
                if respuesta_spearow == True:
                    e.status_ine_loads = 2
                    e.mensaje_error = "Se cargo imagen a DB B"
                    db_session.add(e)
                    db_session.commit()
                    db_session.close()
                    return True
                else:
                    e.status_ine_loads = 0
                    e.mensaje_error = "No se cargo a DB"
                    db_session.add(e)
                    db_session.commit()
                    db_session.close()
                    return False
            else:
                if us is None:
                    a = ResultsIne(
                        user_id=user,
                        email_user=correo,
                        mensaje_error="no se cargaron imagenes a QB",
                        rid_solicitud=rid,
                        status_ine_loads=1,
                    )
                    db_session.add(a)
                    db_session.commit()
                else:
                    us.mensaje_error = "no se cargaron imagenes a QB"
                    us.status_ine_loads = 0
                    db_session.add(us)
                    db_session.commit()
                db_session.close()
                return False

    else:
        return False


def send_sperow(datos):
    try:
        if "status" in datos:
            if datos["status"] == False:
                # datos_insert(datos['user'],0,"",1)
                return jsonify(success=False, message="error 1"), 400
            else:
                # datos_insert(datos['user'],datos['rid'],datos['correo'],2)
                SPEAROW_URI = os.environ.get("SPEAROW_URI")
                headers = {"Content-Type": "application/json"}
                body = datos
                r = requests.post(
                    SPEAROW_URI + "/api/v1/file/img", json=body, headers=headers
                )
                spearoowcodeF = r.status_code
                if spearoowcodeF == 200:
                    return True
                else:
                    return False
        else:
            return False
    except Exception as e:
        capture_exception(e)
        return False


def pld_check(datos):
    user = datos
    cheked = db_session.query(ResultsIne).filter_by(user_id=user).first()
    if cheked == None:
        return 0
    else:
        return cheked.status_ine_loads


def send_economica(datos):
    try:
        result_ine = (
            db_session.query(ResultsIne).filter_by(user_id=datos["user_id"]).first()
        )
        actividad_economica = (
            db_session.query(actividad_economica_sub_cat)
            .filter_by(sub_clave_economica_id=datos["clave_economica_id"])
            .first()
        )
        result_ine.sub_nombre_economica = actividad_economica.sub_nombre_economica
        result_ine.sub_clave_economica_id = actividad_economica.sub_clave_economica_id
        db_session.add(result_ine)
        db_session.commit()
        # db_session.close()
        FLASK_ENV = os.environ.get("FLASK_ENV")
        if FLASK_ENV == "production":
            #send_sf_datos
            send_qb_datos(datos["user_id"])
        else:
            result_ine.status_ine_loads = 3
            db_session.add(result_ine)
            db_session.commit()

        return True
    except Exception as e:
        capture_exception(e)
        return False

def get_token_SF():
    try:
        url = os.environ.get("SF_url_")
        sf_username=os.environ.get("SF_username")
        sf_password=os.environ.get("SF_password")
        sf_grant_type=os.environ.get("SF_grant_type")
        sf_client_id=os.environ.get("SF_client_id")
        sf_client_secret=os.environ.get("SF_client_secret")
        payload = "-----011000010111000001101001\r\nContent-Disposition: form-data;name=\"username\"\r\n\r\n{0}\r\n-----011000010111000001101001\r\nContent-Disposition:form-data; name=\"password\"\r\n\r\n{1}\r\n-----011000010111000001101001\r\nContent-Disposition: form-data; name=\"grant_type\"\r\n\r\n{2}\r\n-----011000010111000001101001\r\nContent-Disposition: form-data; name=\"client_id\"\r\n\r\n{3}\r\n-----011000010111000001101001\r\nContent-Disposition: form-data; name=\"client_secret\"\r\n\r\n{4}\r\n-----011000010111000001101001\r\nContent-Disposition: form-data; name=\"\"\r\n\r\n\r\n-----011000010111000001101001--\r\n".format(sf_username,sf_password,sf_grant_type,sf_client_id,sf_client_secret)
        headers = {
            "cookie": "CookieConsentPolicy=0%3A0; LSKey-c%24CookieConsentPolicy=0%3A0; BrowserId=0jJ5wbbBEe2LNtHLZ8N_vA",
            "Content-Type": "multipart/form-data; boundary=---011000010111000001101001"
        }
        response = requests.request("POST", url, data=payload, headers=headers)
        if response.status_code==200:
            #guardar el token 
            token=response.json()
            access_token=token['access_token']
            instance_url=token['instance_url']
            issued_at=token['issued_at']
            save_token = SF_token(
                    access_token=access_token, 
                    instance_url=instance_url,
                    issued_at=issued_at
                )
            db_session.add(save_token)
            db_session.commit()
            return access_token
    except Exception as e:
        capture_exception(e)
        traceback.print_exc()
        return False

def get_token_SF_db():
    try:
        token = db_session.query(SF_token).order_by(SF_token.id.desc()).first()
        #validamos si existe token
        if token==None:
            token=get_token_SF()
            return token
        return token.access_token
    except Exception as e:
        capture_exception(e)
        traceback.print_exc()
        return False

def send_sf_datos(user):
    try:
        res_ine = db_session.query(ResultsIne).filter_by(user_id=user).first()
        frente=res_ine.front
        back=res_ine.back
        user_id=str(res_ine.user_id)
        user_id = user_id.replace('-','')    
        payload = {
            "email":res_ine.email_user,
            "uuid": user_id,
            "image_front": frente,
            "image_back": back
            }
        token=get_token_SF_db()
        if token:
            #enviamos SalesForce
            url = "https://curadeudamexico--test.sandbox.my.salesforce.com/services/apexrest/v1/Ine/"        
            headers = {
            "cookie": "BrowserId=0jJ5wbbBEe2LNtHLZ8N_vA; CookieConsentPolicy=0%3A1; LSKey-c%24CookieConsentPolicy=0%3A1",
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(token)
            }
            response = requests.request("POST", url, json=payload, headers=headers)
            #print("response",response.json())
            if response.status_code==401:#se valida porque el token murio
                #enviamos SalesForce nuevamente
                token=get_token_SF()                
                url = "https://curadeudamexico--test.sandbox.my.salesforce.com/services/apexrest/v1/Ine/"                
                headers = {
                "cookie": "BrowserId=0jJ5wbbBEe2LNtHLZ8N_vA; CookieConsentPolicy=0%3A1; LSKey-c%24CookieConsentPolicy=0%3A1",
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(token)
                }
                response = requests.request("POST", url, json=payload, headers=headers)
                #print("response else",response.json())
            code=response.status_code
        if code == 200:
            res_ine.status_ine_loads = 3
            db_session.add(res_ine)
            db_session.commit()
            db_session.close()
            return True
        else:
            res_ine.status_ine_loads = 2
            db_session.add(res_ine)
            db_session.commit()
            db_session.close()
            return False
            
    except Exception as e:
        capture_exception(e)
        traceback.print_exc()
        return False

def send_qb_datos(user):
    res_ine = db_session.query(ResultsIne).filter_by(user_id=user).first()
    if res_ine.rid_solicitud == 0:
        res_ine.status_ine_loads = 8
        res_ine.mensaje_error = "Sin rid de solicitud"
        db_session.add(res_ine)
        db_session.commit()
        db_session.close()
        # v={"email":res_ine.email_user,"actividad":res_ine.sub_nombre_economica}
    else:
        # v={"id":res_ine.rid_solicitud,"actividad":res_ine.sub_nombre_economica}

        act = str(res_ine.sub_nombre_economica)
        v = {
            "to": "bgrm6tt7q",
            "data": [
                {
                    "316": {"value": act},
                    "320": {"value": res_ine.front},
                    "321": {"value": res_ine.back},
                    "3": {"value": res_ine.rid_solicitud},
                }
            ],
        }
    USERTOKEN = os.environ.get("USERTOKEN")
    QBR = os.environ.get("QBRealmHostname")
    UserAgent = os.environ.get("UserAgent")

    headers = {
        "QB-Realm-Hostname": QBR,
        "User-Agent": UserAgent,
        "Authorization": "QB-USER-TOKEN {}".format(USERTOKEN),
        "Content-Type": "application/json",
    }
    QB = requests.post("https://api.quickbase.com/v1/records", json=v, headers=headers)
    code = QB.status_code
    # QB = requests.post("https://www.workato.com/webhooks/rest/1b7fa5ec-105e-4422-ad07-4dd0af2c570b/carga-ine-cdd",json=v ,headers=headers)
    # code=QB.status_code

    if code == 200:
        res_ine.status_ine_loads = 3
        db_session.add(res_ine)
        db_session.commit()
        db_session.close()
        return True
    else:
        res_ine.status_ine_loads = 2
        db_session.add(res_ine)
        db_session.commit()
        db_session.close()
        return False


def loads_inicial_actieco(datos):
    data = []
    for a in datos:
        e = actividad_economica(clave_economica=a)
        db_session.add(e)
        db_session.commit()
        data.append({"id": e.id, "acti": a})
    db_session.close()
    dat = {"dat": data, "datos": datos}
    return carga_datos_cat(dat)


def carga_datos_cat(dat):
    Privado = []
    Publico = []
    for a in dat["dat"]:
        if a["acti"] == "SECTOR PRIVADO":
            for b in dat["datos"]["SECTOR PRIVADO"]:
                nombre = str(b)
                privado = actividad_economicaCat(
                    cat_nombre_economica=nombre, cat_actividad_economica_id=a["id"]
                )
                db_session.add(privado)
                db_session.commit()
                Privado.append({"id": privado.id, "cat_nombre": nombre})
                # print(b,a['id'])
            db_session.close()
        elif a["acti"] == "SECTOR PÚBLICO":
            for b in dat["datos"]["SECTOR PÚBLICO"]:
                nombre = str(b)
                publico = actividad_economicaCat(
                    cat_nombre_economica=nombre, cat_actividad_economica_id=a["id"]
                )
                db_session.add(publico)
                db_session.commit()
                Publico.append({"id": publico.id, "cat_nombre": nombre})
                # print(b,a['id'])

            db_session.close()
    da = {"Privado": Privado, "Publico": Publico, "datos": dat["datos"]}
    return carga_datos_cat_sub(da)


def carga_datos_cat_sub(da):

    for a in da["Privado"]:
        nombre = str(a["cat_nombre"])
        for b in da["datos"]["SECTOR PRIVADO"][nombre]:
            id = str(b["id"])
            nombre = str(b["name"])
            privado = actividad_economica_sub_cat(
                sub_nombre_economica=nombre,
                sub_clave_economica_id=id,
                sub_cat_actividad_economica_id=a["id"],
            )
            db_session.add(privado)
            db_session.commit()
        db_session.close()

    for a in da["Publico"]:
        nombre = str(a["cat_nombre"])
        for b in da["datos"]["SECTOR PÚBLICO"][nombre]:
            id = str(b["id"])
            nombre = str(b["name"])
            publico = actividad_economica_sub_cat(
                sub_nombre_economica=nombre,
                sub_clave_economica_id=id,
                sub_cat_actividad_economica_id=a["id"],
            )
            db_session.add(publico)
            db_session.commit()
        db_session.close()


def webhook_handler(data):
    event = data["events"][0]
    date = datetime.datetime.strptime(event["timestamp"], "%Y-%m-%dT%H:%M:%S%fZ")
    webhook = HookLog(
        event["event_type"],
        event["event_action"],
        event["object"],
        event["version"],
        date,
    )
    db_session.add(webhook)
    db_session.commit()
    fill_id(webhook)
    db_session.commit()
    validation_id = webhook.get_validation_id()
    if validation_id:
        fill_validation.delay(validation_id)
    check_id = webhook.get_check_id()
    if check_id:
        fill_check.delay(check_id)
    proccess_id = webhook.detone_download()
    if proccess_id:
        get_link_images.delay(proccess_id)
    final_check = webhook.get_final_check_id()
    if final_check:
        fill_last_check.delay(final_check)


def fill_id(hook: HookLog):
    if hook.get_ids():
        if hook.get_ids().create:
            ids = ProcessID(
                proccess_id=hook.get_ids().process_id,
                account_id=hook.get_ids().account_id,
            )
            db_session.add(ids)
        elif hook.get_ids().update:
            old = (
                db_session.query(ProcessID)
                .filter(ProcessID.proccess_id == hook.get_ids().process_id)
                .first()
            )
            old.validation_id = hook.get_ids().validation_id
        elif hook.get_ids().check_id:
            old = (
                db_session.query(ProcessID)
                .filter(ProcessID.proccess_id == hook.get_ids().process_id)
                .first()
            )
            old.first_check_id = hook.get_ids().check_id


@celery.task()
def fill_validation(validation_id: str):
    try:
        existing_validation = (
            db_session.query(Validation).filter(Validation.id == validation_id).one()
        )
    except NoResultFound:
        headers = {
            "Truora-API-Key": os.environ.get("TRUORA_API_KEY"),
        }
        truora_info = requests.get(
            f"https://api.validations.truora.com/v1/validations/{validation_id}",
            headers=headers,
        )
        if truora_info.status_code == 200:
            validation = Validation(**truora_info.json())
            db_session.add(validation)
            db_session.commit()
            try:
                validation_details = ValidationDetail(
                    validation_id,
                    **truora_info.json().get("details").get("document_details"),
                )
                valid_documents = (
                    truora_info.json().get("details").get("document_validations")
                )

                db_session.add(validation_details)
                if valid_documents:
                    for _, values in valid_documents.items():
                        for value in values:
                            validation_documents = ValidationDocument(
                                validation_id, **value
                            )
                            db_session.add(validation_documents)
                db_session.commit()
            except AttributeError:
                pass
            except Exception as e:
                capture_exception(e)


@celery.task()
def fill_check(check_id: str):
    try:
        old_check = db_session.query(Check).filter(Check.id == check_id).one()
    except NoResultFound:
        headers = {
            "Truora-API-Key": os.environ.get("TRUORA_API_KEY"),
        }
        truora_info = requests.get(
            f"https://api.checks.truora.com/v1/checks/{check_id}", headers=headers
        )
        if truora_info.status_code == 200:
            check = Check(**truora_info.json()["check"])
            db_session.add(check)
            db_session.commit()


@celery.task()
def fill_last_check(check_id: str):
    try:
        last_check_id = (
            db_session.query(ProcessID)
            .filter(ProcessID.last_check_id == check_id)
            .one()
        )
        headers = {
            "Truora-API-Key": os.environ.get("TRUORA_API_KEY"),
        }
        truora_info = requests.get(
            f"https://api.checks.truora.com/v1/checks/{check_id}", headers=headers
        )
        if truora_info.status_code == 200:
            last_check = Check(**truora_info.json()["check"])
            db_session.add(last_check)
            db_session.commit()
            return True
    except NoResultFound:
        return False


@celery.task()
def get_link_images(process_id: str):
    front_url = None
    back_url = None
    validation_id = (
        db_session.query(ProcessID)
        .filter(ProcessID.proccess_id == process_id, ProcessID.validation_id != None)
        .first()
        .validation_id
    )
    process = (
        db_session.query(ProcessID).filter(ProcessID.proccess_id == process_id).first()
    )
    if process:
        headers = {
            "Truora-API-Key": os.environ.get("TRUORA_API_KEY"),
        }
        truora_info = requests.get(
            f"https://api.identity.truora.com/v1/processes/{process_id}/result",
            headers=headers,
        )
        if truora_info.status_code == 200:
            truora_json = truora_info.json()
            if truora_json.get("status") == "success":
                front_url = truora_json.get("validations")[0].get("front_image")
                back_url = truora_json.get("validations")[0].get("reverse_image")
                db_session.query(ValidationDetail).filter(
                    ValidationDetail.validation_id == validation_id
                ).update(
                    {"front_url": front_url, "back_url": back_url},
                    synchronize_session=False,
                )
                db_session.commit()
                return True
        else:
            return False


def link_user_to_process(process_id: str, user_id: str, account_id: str):
    process = (
        db_session.query(ProcessID)
        .filter(ProcessID.proccess_id == process_id, ProcessID.account_id == account_id)
        .first()
    )
    if process:
        process.user_id = user_id
        db_session.commit()
        return process
    else:
        return False


def verify_process_status(process_id: str) -> bool:
    headers = {
        "Truora-API-Key": os.environ.get("TRUORA_API_KEY"),
    }
    truora_info = requests.get(
        f"https://api.identity.truora.com/v1/processes/{process_id}/result",
        headers=headers,
    )
    if truora_info.status_code == 200:
        truora_json = truora_info.json()
        if (
            truora_json.get("status") == "success"
            or truora_json.get("status") == "pending"
        ):
            return True
        else:
            return False
    else:
        return False


def create_result_ine(user_id):
    try:
        result = ResultsIne(user_id=user_id, status_ine_loads=2)
        db_session.add(result)
        db_session.commit()
        return result
    except Exception as e:
        capture_exception(e)
        return False


@celery.task(bind=True)
def download_images(self, validation_id: str, user_id: str, process_id: str = None):
    to_mewtwo_data = {}
    validation_details = (
        db_session.query(ValidationDetail)
        .filter(ValidationDetail.validation_id == validation_id)
        .first()
    )
    front_url = validation_details.front_url
    back_url = validation_details.back_url
    if front_url and back_url:
        front_image = requests.get(front_url)
        back_image = requests.get(back_url)
        if front_image.status_code == 200 and back_image.status_code == 200:
            image_base64_front = base64.b64encode(front_image.content).decode("utf-8")
            image_base64_back = base64.b64encode(back_image.content).decode("utf-8")
            to_mewtwo_data = {
                "front_image": image_base64_front,
                "back_image": image_base64_back,
                "user_id": user_id,
            }
            return to_mewtwo_data
        else:
            get_link_images(process_id)
            self.retry(countdown=3, max_retries=2)
    elif front_url:
        front_image = requests.get(front_url)
        if front_image.status_code == 200:
            image_base64_front = base64.b64encode(front_image.content).decode("utf-8")
            to_mewtwo_data = {
                "front_image": image_base64_front,
                "back_image": image_base64_front,
                "user_id": user_id,
            }
            return to_mewtwo_data
        else:
            get_link_images(process_id)
            self.retry(countdown=3, max_retries=2)
    return None


@celery.task()
def mewtwo_progress_pld(data):
    data_to_send = {
        "front_image": data["front_image"],
        "back_image": data["back_image"],
        "user_id": data["user_id"],
    }
    mewtwo_info = requests.post(
        f"{os.environ.get('MEWTOW_URI')}/loadsImagesIne", json=data_to_send
    )
    return True


@celery.task()
def create_customer_check(user_id: str) -> bool:
    try:
        process = db_session.query(ProcessID).filter(ProcessID.user_id == user_id).one()
    except NoResultFound:
        return False
    except MultipleResultsFound:
        process = (
            db_session.query(ProcessID)
            .filter(ProcessID.user_id == user_id, ProcessID.validation_id != None)
            .first()
        )
    validation_id = process.validation_id
    if curp := get_user_document_number(validation_id):
        payload = f"country=MX&type=person&national_id={curp}&user_authorized=true&owner_document_type=national_id"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Truora-API-Key": os.environ.get("TRUORA_API_KEY"),
            "truora-priority": "medium",
        }
        check = requests.post(
            "https://api.checks.truora.com/v1/checks", data=payload, headers=headers
        )
        check_json = check.json()
        new_check_id = check_json["check"].get("check_id")
        process.last_check_id = new_check_id
        db_session.commit()
        get_bad_score.delay(new_check_id, user_id)
        return True
    else:
        return False

@celery.task(bind=True)
def get_bad_score(self, check_id: str, user_id: str) -> bool:
    try:
        queryCheckID = db_session.query(Check).filter(Check.id == check_id, Check.score < 0.5, Check.type == "person").one()
        user_Name = queryCheckID.summary
        name = f"{user_Name.get('names_found')[0].get('first_name')} {user_Name.get('names_found')[0].get('last_name')}"
        dataEmailandRid = get_user_info(user_id)
        data = {
            "subject": "Score bajo KYC",
            "personalization": {
                "name": name,
                "email": dataEmailandRid.email_user,
                "rid_solicitud": dataEmailandRid.rid_solicitud,
            }
        }
        save_pdf_check(check_id)
        send_email(data,check_id)
        return True
    except NoResultFound:
        self.retry(countdown=30, max_retries=2)


def save_pdf_check(check_id:str):
    try:
        headers = {
            "Truora-API-Key": os.environ.get("TRUORA_API_KEY"),
        }
        r = requests.get(f"https://api.checks.truora.com/v1/checks/{check_id}/pdf", headers=headers)
        if r.status_code == 200:
            pdf = r.content
            with open(f"{check_id}.pdf", "wb") as f:
                f.write(pdf)
            return True
        else:
            return None
    except Exception as e:
        capture_exception(e)
        return None


def open_pdf(check_id:str):
    """
    Open a pdf and return a base64 encoded string
    """
    try:
        with open(f"{check_id}.pdf", "rb") as f:
            pdf = f.read()
            pdf_base64 = base64.b64encode(pdf).decode("utf-8")
            return pdf_base64
    except Exception as e:
        capture_exception(e)
        return None


def send_email(data,check_id):
    try:
        headers = {
            "Content-Type": "application/json",
        }
        json_data = {
            **data,
            "pdf": open_pdf(check_id),
        }
        r = requests.post("https://www.workato.com/webhooks/rest/1b7fa5ec-105e-4422-ad07-4dd0af2c570b/pdf-score", json=json_data, headers=headers)
        print(r.status_code)
    except Exception as e:
        traceback.print_exc()
        capture_exception(e)
        return None



def get_user_info(userId):
    try:
        queryCheckID = (db_session.query(ResultsIne).filter(ResultsIne.user_id == userId).one())
        return queryCheckID
    except NoResultFound:
        return False

def get_user_document_number(validation_id: str) -> str:
    details = (
        db_session.query(ValidationDetail)
        .filter(ValidationDetail.validation_id == validation_id)
        .first()
    )
    return details.document_number

def get_nombre_act_economica(user_id):
    try:
        data = db_session.query(ResultsIne).filter(ResultsIne.user_id == user_id).one()
        return data.sub_nombre_economica
    except MultipleResultsFound:
        data = (
            db_session.query(ResultsIne)
            .filter(ResultsIne.user_id == user_id)
            .order_by(ResultsIne.created_at.desc())
            .first()
        )
        return data.sub_nombre_economica
    except NoResultFound:
        return None
