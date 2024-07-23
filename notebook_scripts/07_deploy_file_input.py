import io
import pickle

import pandas as pd
import uvicorn
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse

from mlops import logger
from mlops.util_funcs import scrub_data


def load_model():
    """Load a model from a pickle file."""
    logger.info("Loading model...")
    with open('model.pkl', 'rb') as file:
        model = pickle.load(file)
        logger.info("Model loaded successfully")
    return model


def predict_responses(features):
    """Predict responses using the loaded model."""
    model = load_model()
    logger.info("Predicting responses...")
    y_pred = model.predict(features)
    return y_pred


app = FastAPI()


@app.get('/')
def route_page():
    """Welcome page notification."""
    return {"message": "Welcome to the Customer Response Prediction API"}


@app.post("/upload")
async def upload_predict(file: UploadFile = File(...)):
    """Handle CSV file uploads for predictions."""

    # check if file is CSV
    if not file.filename.endswith(".csv"):
        return {"error": "File is not a CSV"}

    # read all the content CSV file
    contents = await file.read()

    # create a pandas DataFrame from the CSV data
    df = pd.read_csv(io.StringIO(contents.decode("utf-8")))

    # prepare data for prediction
    cleaned_data = scrub_data(df).to_dict(orient='records')
    response_ = predict_responses(cleaned_data)
    df['PredResponse'] = response_

    # save the result to a new CSV file
    output_file = "predictions.csv"
    df.to_csv(output_file, index=False)

    logger.info('Returning predictions as csv file: %s', output_file)
    return FileResponse(output_file, filename=output_file)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
