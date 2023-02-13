from app.kyc.controllers import (fill_ocr_result, fill_score, start_process, validate_information, validate_process,
                                 validate_score, get_curp)
from flask import Blueprint, jsonify, request

kyc = Blueprint("kyc", __name__, url_prefix="/kyc")


@kyc.route("/start", methods=["POST"])
def start_kyc():
    print("que rayos")
    print("que user id se envia",request.json["user_id"])
    url = start_process(request.json["user_id"])
    return jsonify(success=True, url=url), 200


@kyc.route("/webhook", methods=["POST"])
def webhook_handler():
    print("webhook",request.json)
    interview_id = request.json["interviewId"]
    if request.json["onboardingStatus"] == "ONBOARDING_FINISHED":
        fill_ocr_result.delay(interview_id)
        fill_score.apply_async(args=[interview_id], link=validate_score.s())
    return jsonify(success=True), 200


@kyc.route("/validate_score/<session_id>", methods=["GET"])
def validate_score_handler(session_id):
    if validate_process(session_id):
        return jsonify(success=True), 200
    else:
        return jsonify(success=False), 400
    

@kyc.route("/correct", methods=["POST"])
def correct_name():
    data = request.json
    validate = validate_information(data['user_id'],data['session_id'])
    return jsonify(success=True, validate=validate), 200
    


@kyc.route("/curp/<user_id>", methods=["GET"])
def get_curp_user(user_id):
    curp = get_curp(user_id)
    return jsonify(success=True, curp=curp), 200