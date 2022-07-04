from app.kyc.controllers import (fill_ocr_result, fill_score, start_process,
                                 validate_score)
from flask import Blueprint, jsonify, request

kyc = Blueprint("kyc", __name__, url_prefix="/kyc")


@kyc.route("/start", methods=["POST"])
def start_kyc():
    url = start_process(request.json["user_id"])
    return jsonify(success=True, url=url), 200


@kyc.route("/webhook", methods=["POST"])
def webhook_handler():
    print(request.json)
    if request.json["onboardingStatus"] == "ONBOARDING_FINISHED":
        fill_ocr_result.delay(request.json["interviewId"])
        fill_score.apply_async((request.json["interviewId"]), link=validate_score.s())
    return jsonify(success=True), 200


@kyc.route("/validate_score/<session_id>", methods=["GET"])
def validate_score_handler(session_id):
    # if validate_process(session_id):
    #     validate_score(session_id)
    #     return jsonify(success=True), 200
    # else:
    #     return jsonify(success=False), 400
    return jsonify(success=True), 200
