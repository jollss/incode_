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


def datos_mewtwo(datos):
    e = db_session.query(ResultsIne).filter_by(user_id=datos['user']).first()
    if e==None:
        a = ResultsIne(
            user_id=datos['user'],
            email_user=datos['correo'],
            rid_solicitud=datos['rid_solicitud']
        )
        db_session.add(a)
        db_session.commit()
        db_session.close()
    else:
        e.email_user =datos['correo']
        e.rid_solicitud=datos['rid_solicitud']
        db_session.add(e)
        db_session.commit()
        db_session.close()
    SPEAROW_URI = os.environ.get('SPEAROW_URI')
    headers = {'Content-Type': "application/json"}
    data={'user_id':datos['user'],'back_image':datos['back'],'front_image':datos['frente']}
    r = requests.post(SPEAROW_URI+"/api/v1/file/img",json=data ,headers=headers)
    spearoowcodeF=r.status_code 
    if spearoowcodeF==200:
        json_data = r.json()
        r=send_abra(json_data)
        if r==True:
            return True
        else:
            return False
    else:
        return False


def send_abra(data):
    l = db_session.query(ResultsIne).filter_by(user_id=data['message']).first()
    try:  
        ABRA_URI = os.environ.get('ABRA_URI')
        if 'imageF' in data['response']:
            headers = {'Content-Type': "application/json"}
            body = {"url":data['response']['imageF']}
            g = requests.post(ABRA_URI+"/api/v1/url",json=body ,headers=headers)
            abracode=g.status_code
            if abracode==200:
                gjson_data = g.json()
                l.front =gjson_data['url']

        if 'imageB' in data['response']:
            headers = {'Content-Type': "application/json"}
            body = {"url":data['response']['imageB']}
            g = requests.post(ABRA_URI+"/api/v1/url",json=body ,headers=headers)
            abracode=g.status_code
            if abracode==200:
                gjson_data = g.json()
                l.back =gjson_data['url']
        l.status_ine_loads=2
        db_session.add(l)
        db_session.commit()
        return True
    except:
        return False

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
            FLASK_ENV = os.environ.get('FLASK_ENV')
            if FLASK_ENV=='production':

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
            else:
                codeF=200
                rid=123
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
            FLASK_ENV = os.environ.get('FLASK_ENV')
            if FLASK_ENV=='production':
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
            else:
                codeF=200
                rid=123
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


def send_economica(datos):
    try:
        result_ine=db_session.query(ResultsIne).filter_by(user_id=datos['user_id']).first()
        actividad_economica=db_session.query(actividad_economica_sub_cat).filter_by(sub_clave_economica_id=datos['clave_economica_id']).first()
        result_ine.sub_nombre_economica = actividad_economica.sub_nombre_economica
        result_ine.sub_clave_economica_id = actividad_economica.sub_clave_economica_id
        db_session.add(result_ine)
        db_session.commit()
        #db_session.close()
        FLASK_ENV = os.environ.get('FLASK_ENV')
        if FLASK_ENV=='production':
            send_qb_datos(datos['user_id'])
        else:
            result_ine.status_ine_loads = 3
            db_session.add(result_ine)
            db_session.commit()

        

        return True
    except:
        return False


def send_qb_datos(user):
    res_ine=db_session.query(ResultsIne).filter_by(user_id=user).first()
    if res_ine.rid_solicitud==0:
        res_ine.status_ine_loads = 8
        res_ine.mensaje_error="Sin rid de solicitud"
        db_session.add(res_ine)
        db_session.commit()
        db_session.close()
        #v={"email":res_ine.email_user,"actividad":res_ine.sub_nombre_economica}
    else:
        #v={"id":res_ine.rid_solicitud,"actividad":res_ine.sub_nombre_economica}
    
        act=str(res_ine.sub_nombre_economica)
        v={'to':'bgrm6tt7q','data':[
                {
                '316':{'value':act},
                '320':{'value':res_ine.front},
                '321':{'value':res_ine.back},
                '3':{'value':res_ine.rid_solicitud}
                }
                                    ]
            }
    USERTOKEN = os.environ.get('USERTOKEN')
    QBR = os.environ.get('QBRealmHostname')
    UserAgent = os.environ.get('UserAgent')

    headers = {
        'QB-Realm-Hostname':QBR,
        'User-Agent':UserAgent,
        'Authorization':'QB-USER-TOKEN {}'.format(USERTOKEN),
        'Content-Type': "application/json"
        }
    QB = requests.post("https://api.quickbase.com/v1/records",json=v,headers=headers)
    code=QB.status_code    
    #QB = requests.post("https://www.workato.com/webhooks/rest/1b7fa5ec-105e-4422-ad07-4dd0af2c570b/carga-ine-cdd",json=v ,headers=headers)
    #code=QB.status_code
    
    if code==200:
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
    data=[]
    for a in datos:        
        e=actividad_economica(
        clave_economica=a
        )
        db_session.add(e)
        db_session.commit()
        data.append({'id':e.id,'acti':a})
    db_session.close()
    dat={"dat":data,'datos':datos}
    return carga_datos_cat(dat)
    
def carga_datos_cat(dat):
    Privado=[]
    Publico=[]
    for a in dat['dat']:        
        if a['acti']=='SECTOR PRIVADO':
            for b in dat['datos']['SECTOR PRIVADO']:
                nombre=str(b)
                privado=actividad_economicaCat(
                    cat_nombre_economica=nombre,
                    cat_actividad_economica_id=a['id']
                )
                db_session.add(privado)
                db_session.commit()
                Privado.append({'id':privado.id,'cat_nombre':nombre})
                #print(b,a['id'])
            db_session.close()                
        elif a['acti']=='SECTOR PÚBLICO':
            for b in dat['datos']['SECTOR PÚBLICO']:
                nombre=str(b)
                publico=actividad_economicaCat(
                    cat_nombre_economica=nombre,
                    cat_actividad_economica_id=a['id']
                )
                db_session.add(publico)
                db_session.commit()
                Publico.append({'id':publico.id,'cat_nombre':nombre})
                #print(b,a['id'])
        
            db_session.close()
    da={"Privado":Privado,'Publico':Publico,'datos':dat['datos']}
    return carga_datos_cat_sub(da)




def carga_datos_cat_sub(da):
    
    for a in da['Privado']:            
        nombre=str(a['cat_nombre'])
        for b in da['datos']['SECTOR PRIVADO'][nombre]:
            id=str(b['id'])
            nombre=str(b['name'])
            privado=actividad_economica_sub_cat(
                    sub_nombre_economica=nombre,
                    sub_clave_economica_id=id,
                    sub_cat_actividad_economica_id=a['id']
                )
            db_session.add(privado)
            db_session.commit()
        db_session.close()
            
    for a in da['Publico']:            
        nombre=str(a['cat_nombre'])
        for b in da['datos']['SECTOR PÚBLICO'][nombre]:
            id=str(b['id'])
            nombre=str(b['name'])
            publico=actividad_economica_sub_cat(
                    sub_nombre_economica=nombre,
                    sub_clave_economica_id=id,
                    sub_cat_actividad_economica_id=a['id']
                )
            db_session.add(publico)
            db_session.commit()
        db_session.close()
            #print("subcateogia",b['name'],b['id'],a['id'])