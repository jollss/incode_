import os
import requests
from app.kyc.models import (
    CurpVerification,
    IdOcrConfidence,
    IdValidation,
    OCRResult,
    Score,
    Session,
)
from app.tasks import celery
from app.database import db_session
from sqlalchemy.orm.exc import NoResultFound


def start_process(user_id):
    session = Session(user_id=user_id)
    session.start()
    try:
        exists_session = (
            db_session.query(Session)
            .filter(Session.session_id == session.session_id)
            .one()
        )
        exists_session.increment_retries()
        exists_session.token = session.token
        db_session.commit()
        return exists_session.url
    except NoResultFound:
        session.set_url()
        session.set_status()
        db_session.add(session)
        db_session.commit()
        return session.url


@celery.task()
def fill_ocr_result(session_id):
    session = db_session.query(Session).filter(Session.session_id == session_id).one()
    session.set_status()
    db_session.commit()
    ocr_data = session.get_ocr_by_token()
    print(ocr_data)
    ocr = OCRResult(session_id=session.id, **ocr_data)
    db_session.add(ocr)
    db_session.commit()


@celery.task()
def fill_score(session_id):
    session = db_session.query(Session).filter(Session.session_id == session_id).one()
    scores_data = session.get_scores_by_token()
    value = scores_data["overall"].get("value")
    status = scores_data["overall"].get("status")
    print(scores_data)
    id_validation_id = IdValidation(**scores_data.get("idValidation"))
    db_session.add(id_validation_id)
    curp_verification_id = CurpVerification(**scores_data.get("curpVerification"))
    db_session.add(curp_verification_id)
    id_ocr_confidence_id = IdOcrConfidence(**scores_data.get("idOcrConfidence"))
    db_session.add(id_ocr_confidence_id)
    db_session.commit()
    scores = Score(
        session_id=session.id,
        id_validation=id_validation_id.id,
        curp_verification=curp_verification_id.id,
        id_ocr_confidence=id_ocr_confidence_id.id,
        value=value,
        status=status,
    )
    db_session.add(scores)
    db_session.commit()


def validate_score(session_id):
    try:
        session = db_session.query(Session,Score).join(Score).filter(Session.session_id == session_id, Score.overall_value > 70, Score.overall_status == "OK").one()
        images = session.Session.get_images()
        mewtwo_progress_pld.delay(session.Session.user_id, images.front, images.back)
        return True
    except NoResultFound:
        return False

@celery.task()
def mewtwo_progress_pld(user_id, front_image, back_image):
    data_to_send = {
        "user_id": str(user_id),
        "front_image": front_image,
        "back_image": back_image,
    }
    mewtwo_info = requests.post(
        f"{os.environ.get('MEWTOW_URI')}/loadsImagesIne", json=data_to_send
    )
    return True


def validate_process(session_id):
    try:
        session = db_session.query(Session,Score).join(Score).filter(Session.session_id == session_id, Score.overall_value > 70, Score.overall_status == "OK").one()
        return True
    except NoResultFound:
        return False