from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, session, abort, send_from_directory, Blueprint

from app.kyc.controllers import fill_ocr_result, fill_score, start_process, validate_score


kyc = Blueprint('kyc', __name__, url_prefix='/kyc')

@kyc.route('/start', methods=['POST'])
def start_kyc():
    start_process(request.json['user_id'])
    return jsonify(success=True), 200


@kyc.route('/webhook', methods=['POST'])
def webhook_handler():
    if request.json['onboardingStatus'] == 'ONBOARDING_FINISHED':
        fill_ocr_result.delay(request.json['interviewId'])
        fill_score.delay(request.json['interviewId'])
    return jsonify(success=True), 200


@kyc.route('/fill_test', methods=['POST'])
def fill_test_handler():
    return jsonify(success=True), 200

@kyc.route('/validate_score', methods=['POST'])
def validate_score_handler():
    validate_score(request.json['session_id'])
    return jsonify(success=True), 200