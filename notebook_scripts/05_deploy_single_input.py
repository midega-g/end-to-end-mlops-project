#!/usr/bin/env python
# coding: utf-8

from mlops.project_libraries import FastAPI, mlflow, os, pd, uvicorn
import pickle
from mlops import logger
from mlops.util_funcs import scrub_data, PredictionRequest


# fill in AWS profile
os.environ["AWS_PROFILE"] = "demiga-g"

# Setting tracking uri (unique resource identifier)
# TRACKING_SERVER_HOST = '127.0.0.1'  # '16.171.136.194'
# mlflow.set_tracking_uri(f"http://{TRACKING_SERVER_HOST}:5000")

# experiment_id = 1
# run_id = '356a23fb4fc54b62bd12ffd56355ed89'

logger.info("Finished loading the required modules and variables")

def load_model():
    """Load a model from an experiment run."""
    # logger.info("Loading model from experiment ID %s, run ID %s", experiment_id, run_id)
    # base_location = 's3://midega-mlflow-artifacts' #'mlflow-artifacts:'  # 's3://midega-mlflow-artifacts'
    # logged_model = f"{base_location}/{experiment_id}/{run_id}/artifacts/model"
    # return mlflow.pyfunc.load_model(logged_model)
    with open('model.pkl', 'rb') as file:
        model = pickle.load(file)
    return model


def predict_responses(features):
    logger.info("Predicting responses...")
    model = load_model()
    y_pred = model.predict(features)
    return y_pred[0]


app = FastAPI()

@app.get('/')
def route_page():
    logger.info("Accessing route page...")
    return {"message": "Welcome to the Customer Response Prediction API"}


@app.post('/predictions')
def predict_endpoint(request: PredictionRequest):
    """
    This function handles prediction requests by accepting a POST request with a PredictionRequest object.
    It extracts the details from the request, prepares the data for prediction, calls the predict_responses function,
    and returns the prediction results.

    Parameters:
    request (PredictionRequest): An instance of PredictionRequest containing the details for prediction.

    Returns:
    dict: A dictionary containing the prediction results. The dictionary has a single key-value pair:
          'response': A list containing the predicted response.
    """
    details = request.dict()
    logger.info("Received prediction request with details: %s", details)

    features = pd.DataFrame([details])
    cleaned_features = scrub_data(features).to_dict(orient='records')
    preds = predict_responses(cleaned_features)
    
    result = {'response': preds.tolist()}
    logger.info("Returning prediction results: %s", result)
    return result


# Run the application when the script is executed directly.
if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=9696)

