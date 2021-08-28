from flask import Flask, current_app, jsonify, request, url_for, render_template
from werkzeug.exceptions import HTTPException, InternalServerError
from app.controllers import *
from app.database import db_session
from flask_cors import CORS



def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')
    CORS(app)


    @app.route("/ping", methods=['GET'])
    def ping():
        return jsonify(success=True,response="pong!"), 200

#---------------------------1 paso obtener la imagenes del ine front y back
    @app.route("/loads-ine", methods=('GET', 'POST'))
    def loadsIne():
        if request.method == "GET":
            return jsonify(success=True,response="Wrong"), 404
        else:
            datos = request.get_json()
            if 'status' in datos:
                if datos['status']==True:
                    if 'front_image' in datos['datos']:
                        q=data_endf=send_qbF(datos['datos']['front_image'],datos['user'],datos['correo'],datos['rid'])
                        if q==False:
                            return jsonify(success=False), 400
                        else:
                            if 'back_image' in datos['datos']:
                                n=data_endb=send_qbB(datos['datos']['back_image'],datos['user'],datos['correo'],datos['rid'])
                            
                                if n==False:
                                    return jsonify(success=False), 400
                                else:
                                    return jsonify(success=True), 200                    
                    return jsonify(success=True), 200
                else:
                    return jsonify(success=False), 400                
            else:
                return jsonify(success=False,response="Error!"), 400
#-----------------------------

    @app.route("/loads-actieco", methods=('GET', 'POST'))
    def loadsActeco():
        if request.method == "GET":
            return False
        else:
            datos = request.get_json() 
            ditto_eco=send_economica(datos)
            datos={"datos":ditto_eco}
            return datos

    @app.route("/pldStatus", methods=('GET', 'POST'))
    def PldStatus():
        if request.method == "GET":
            return False
        else:
            datos = request.get_json() 
            check_status=pld_check(datos)
            return jsonify(success=True,response=check_status), 200
    
    @app.errorhandler(Exception)
    def handle_exception(e):
        return jsonify(success=False, error_message="{}".format(e)), 500

    @app.errorhandler(HTTPException)
    def handle_bad_request(e):
        return jsonify(success=False, error_message="{}".format(e)), e.code
    
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.remove()

    return app
