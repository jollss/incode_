# import logging
import newrelic.agent
import sentry_sdk
from flask import Flask, current_app, jsonify, render_template, request, url_for
from flask.wrappers import Response
from flask_cors import CORS
from sentry_sdk import capture_exception, capture_message
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from werkzeug.exceptions import HTTPException, InternalServerError
from app.kyc import kyc
from app.controllers import *
from app.database import db_session


def traces_sampler(sampling_context):
    if os.environ.get("FLASK_ENV") == "development":
        return 1
    else:
        return 0.3


def create_app():
    sentry_sdk.init(
        dsn="https://34bc7ac43cae484ba8cacff8bd791b84@sentry.curadeuda.com/12",
        integrations=[
            FlaskIntegration(transaction_style="url"),
            SqlalchemyIntegration(),
        ],
        environment=os.environ.get("FLASK_ENV"),
        send_default_pii=True,
        # release='cyndaquil@latest',
        traces_sample_rate=1,
    )
    app = Flask(__name__)
    app.config.from_object("app.config.Config")
    app.register_blueprint(kyc)
    CORS(app)
    # logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',filename='./logs/app.log')

    @app.route("/ping", methods=["GET"])
    def ping():
        print("entro a ping")
        return jsonify(success=True, response="pong!"), 200

    @app.route("/Get_token_SF", methods=["GET"])
    def get_token_sf():
        try:
            #headers para que no cualquiera entre en teoria
            if request.headers['X-Cyndaquill-Key'] == current_app.config['TOKEN_SF_KEY']:
                token=get_token_SF_db()
                if token:
                    return jsonify(success=True, response=token), 200
                return jsonify(success=False,error_code=4003,response="uppss"), 400
                #4001 Not authorized and 401 code http or https
                #4002 propio de catch
            return jsonify(success=False,error_code=4002,response="wrong token"), 400
        except Exception as e:
            capture_exception(e)
            traceback.print_exc()
            return jsonify(success=False,error_code=4001,response="Not authorized"), 401

    @app.route("/loads-ine", methods=["POST"])
    def loadsInes():

        datos = request.get_json()
        if "status" in datos:
            if datos["status"] == True:
                v = datos_mewtwo(datos)
                if v == True:
                    return jsonify(success=True), 200
                else:
                    return jsonify(success=False), 400
            else:
                return jsonify(success=False, reponse=datos), 400

    # ---------------------------1 paso obtener la imagenes del ine front y back
    """@app.route("/loads-ine", methods=('GET', 'POST'))
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
                return jsonify(success=False,response="Error!"), 400"""
    # -----------------------------

    @app.route("/loads-actieco", methods=("GET", "POST"))
    def loadsActeco():
        if request.method == "GET":
            return False
        else:
            datos = request.get_json()
            ditto_eco = send_economica(datos)
            datos = {"datos": ditto_eco}
            return datos

    @app.route("/pldStatus", methods=("GET", "POST"))
    def PldStatus():
        if request.method == "GET":
            return False
        else:
            datos = request.get_json()
            check_status = pld_check(datos)
            return jsonify(success=True, response=check_status), 200

    @app.route("/carga-inicial-actieco", methods=("GET", "POST"))
    def loadsInicialActeco():
        if request.method == "GET":
            return False
        else:
            datos = request.get_json()
            loadsinact = loads_inicial_actieco(datos)
            return jsonify(success=True, response="pong!"), 200
            # datos={"datos":ditto_eco}
            # return datos


    @app.route("/act_eco/<user_id>", methods=["GET"])
    def get_act_eco(user_id):
        act_name = get_nombre_act_economica(user_id)
        if act_name:
            return jsonify(success=True, response=act_name), 200
        else:
            return jsonify(success=False, response="No existe"), 404


    @app.errorhandler(Exception)
    def handle_exception(e):
        capture_exception(e)
        traceback.print_exc()
        return jsonify(success=False, error_message="{}".format(e)), 500

    @app.errorhandler(HTTPException)
    def handle_bad_request(e):
        capture_exception(e)
        return jsonify(success=False, error_message="{}".format(e)), e.code

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.remove()

    return app
