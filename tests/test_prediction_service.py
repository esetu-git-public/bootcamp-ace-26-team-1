from unittest.mock import patch
from app.services.prediction_service import predict_single


def test_predict_single_success():

    patient = {
        "patient_id": 1,
        "age": 65,
        "gender": "Male"
    }

    expected_result = {
        "risk_score": 0.92,
        "risk_label": "High Risk"
    }

    with patch("app.services.prediction_service.predictor.predict_one") as mock_predict, \
         patch("app.services.prediction_service.db.insert_prediction") as mock_db:

        mock_predict.return_value = expected_result

        result = predict_single(patient, created_by="doctor@test.com")

        assert result == expected_result

        mock_predict.assert_called_once_with(patient)

        mock_db.assert_called_once()


def test_predict_single_low_risk():

    patient = {
        "patient_id": 2,
        "age": 35,
        "gender": "Female"
    }

    expected_result = {
        "risk_score": 0.20,
        "risk_label": "Low Risk"
    }

    with patch("app.services.prediction_service.predictor.predict_one") as mock_predict, \
         patch("app.services.prediction_service.db.insert_prediction") as mock_db:

        mock_predict.return_value = expected_result

        result = predict_single(patient, created_by="doctor@test.com")

        assert result["risk_label"] == "Low Risk"

        mock_db.assert_called_once()


def test_predict_single_without_patient_id():

    patient = {
        "age": 50,
        "gender": "Male"
    }

    expected_result = {
        "risk_score": 0.55,
        "risk_label": "Medium Risk"
    }

    with patch("app.services.prediction_service.predictor.predict_one") as mock_predict, \
         patch("app.services.prediction_service.db.insert_prediction") as mock_db:

        mock_predict.return_value = expected_result

        result = predict_single(patient, created_by="doctor@test.com")

        assert result["risk_label"] == "Medium Risk"

        mock_db.assert_called_once()


def test_predict_single_prediction_exception():

    patient = {
        "patient_id": 1,
        "age": 65
    }

    with patch("app.services.prediction_service.predictor.predict_one") as mock_predict:

        mock_predict.side_effect = Exception("Prediction Failed")

        try:
            predict_single(patient, created_by="doctor@test.com")
            assert False
        except Exception as e:
            assert str(e) == "Prediction Failed"