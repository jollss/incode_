import os
from os import path
import pytz
import sys
import string
import requests
import base64
from flask import render_template,jsonify
from weasyprint import HTML
from sqlalchemy.sql.expression import false
sys.path = ['', '..'] + sys.path[1:]
import datetime

from base64 import b64encode

from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.orm.exc import NoResultFound 
from app.models import *

import calendar
from json.decoder import JSONDecodeError
import time
from app.database import db_session
from flask import Flask, request
import base64
from PIL import Image
import io
from os import remove


def send_qbF(frente="",user="",correo="",rid=""):
    tam_frente=len(frente)
    d=datetime.datetime.now(tz=tz).strftime('%Y%m%d')
    carpeta="app/ineImages/"
    if tam_frente>0:
        n=str(user) 
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
            datafrente={'to':'bgrm6tt7q','data':[{#'281':{'value':{'fileName':f"atras {result_ine.rid_solicitud}.jpeg" ,'data':back}},
                '79':{'value':{'fileName':f"frente {rid}.{ext}",'data':imgf}},'3':{'value':rid}}] }
            USERTOKEN = os.environ.get('USERTOKEN')
            QBR = os.environ.get('QBRealmHostname')
            UserAgent = os.environ.get('UserAgent')

            headers = {
                'QB-Realm-Hostname':QBR,
                'User-Agent':UserAgent,
                'Authorization':'QB-USER-TOKEN {}'.format(USERTOKEN),
                'Content-Type': "application/json"
                }
            QBINeF = requests.post("https://api.quickbase.com/v1/records",json=datafrente,headers=headers)
            codeF=QBINeF.status_code
            us = db_session.query(ResultsIne).filter_by(user_id=user).first()
            if codeF==200:
                if us is None:
                    a = ResultsIne(
                                user_id=user,
                                email_user=correo,
                                mensaje_error="se cargaron imagenes a QB",
                                rid_solicitud=rid,
                                status_ine_loads=1
                            )
                    db_session.add(a)
                    db_session.commit()
                else:
                    us.mensaje_error ="se cargaron imagenes a QB"
                    us.status_ine_loads=1
                    db_session.add(us)
                    db_session.commit()
                db_session.close()
                data_sperow={'correo':correo,'rid':rid,'status':True,"front_image":frente,'user':user}
                respuesta_spearow=send_sperow(data_sperow)
                e = db_session.query(ResultsIne).filter_by(user_id=user).first()
                if respuesta_spearow==True:                    
                    e.status_ine_loads=2
                    e.mensaje_error ="Se cargo imagen a DB F"
                    db_session.add(e)
                    db_session.commit()
                    db_session.close()
                    return True
                else:
                    e.status_ine_loads=4
                    e.mensaje_error ="No se cargo a DB"
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
                                    status_ine_loads=1
                                )
                    db_session.add(a)
                    db_session.commit()
                else:
                    us.mensaje_error ="no se cargaron imagenes a QB"
                    us.status_ine_loads=0
                    db_session.add(us)
                    db_session.commit()
                db_session.close()
                return False

    else:
        return False


def send_qbB(atras="",user="",correo="",rid=""):
    tam_atras=len(atras)
    d=datetime.datetime.now(tz=tz).strftime('%Y%m%d')
    carpeta="app/ineImages/"
    if tam_atras>0:
        n=str(user) 
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
            datafrente={'to':'bgrm6tt7q','data':[{#'79':{'value':{'fileName':f"atras {result_ine.rid_solicitud}.jpeg" ,'data':back}},
                '281':{'value':{'fileName':f"atras {rid}.{ext}",'data':imgb}},'3':{'value':rid}}] }
            USERTOKEN = os.environ.get('USERTOKEN')
            QBR = os.environ.get('QBRealmHostname')
            UserAgent = os.environ.get('UserAgent')

            headers = {
                'QB-Realm-Hostname':QBR,
                'User-Agent':UserAgent,
                'Authorization':'QB-USER-TOKEN {}'.format(USERTOKEN),
                'Content-Type': "application/json"
                }
            QBINeF = requests.post("https://api.quickbase.com/v1/records",json=datafrente,headers=headers)
            codeF=QBINeF.status_code
            us = db_session.query(ResultsIne).filter_by(user_id=user).first()
            if codeF==200:
                if us is None:
                    a = ResultsIne(
                                user_id=user,
                                email_user=correo,
                                mensaje_error="se cargaron imagenes a QB",
                                rid_solicitud=rid,
                                status_ine_loads=1
                            )
                    db_session.add(a)
                    db_session.commit()
                else:
                    us.mensaje_error ="se cargaron imagenes a QB"
                    us.status_ine_loads=1
                    db_session.add(us)
                    db_session.commit()
                db_session.close()
                data_sperow={'correo':correo,'rid':rid,'status':True,"back_image":atras,'user':user}
                respuesta_spearow=send_sperow(data_sperow)
                e = db_session.query(ResultsIne).filter_by(user_id=user).first()
                if respuesta_spearow==True:                    
                    e.status_ine_loads=2
                    e.mensaje_error ="Se cargo imagen a DB B"
                    db_session.add(e)
                    db_session.commit()
                    db_session.close()
                    return True
                else:
                    e.status_ine_loads=0
                    e.mensaje_error ="No se cargo a DB"
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
                                    status_ine_loads=1
                                )
                    db_session.add(a)
                    db_session.commit()
                else:
                    us.mensaje_error ="no se cargaron imagenes a QB"
                    us.status_ine_loads=0
                    db_session.add(us)
                    db_session.commit()
                db_session.close()
                return False

    else:
        return False


def send_sperow(datos):
    try:
        if 'status' in datos:
            if datos['status']==False:     
                #datos_insert(datos['user'],0,"",1)
                return jsonify(success=False, message="error 1"), 400            
            else:
                #datos_insert(datos['user'],datos['rid'],datos['correo'],2)
                SPEAROW_URI = os.environ.get('SPEAROW_URI')
                headers = {'Content-Type': "application/json"}
                body = datos
                r = requests.post(SPEAROW_URI+"/api/v1/file/img",json=body ,headers=headers)
                spearoowcodeF=r.status_code                
                if spearoowcodeF==200:                    
                    return True
                else:                    
                    return False
        else:
            return False
    except:
        return False


def pld_check(datos):
    user=datos
    cheked = db_session.query(ResultsIne).filter_by(user_id=user).first()    
    if cheked==None:
        return 0
    else:
        return cheked.status_ine_loads