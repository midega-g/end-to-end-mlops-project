import io
import pickle

import pandas as pd
import uvicorn
from fastapi import File, FastAPI, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from mlops import logger
from mlops.util_funcs import scrub_data

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/data", StaticFiles(directory="data"), name="data")

templates = Jinja2Templates(directory="templates")


def load_model():
    """Load a model from a pickle file."""
    logger.info("Loading model...")
    with open('model/model.pkl', 'rb') as file:
        model = pickle.load(file)
        logger.info("Model loaded successfully")
    return model


def predict_responses(features):
    """Predict responses using the loaded model."""
    model = load_model()
    logger.info("Predicting responses...")
    y_pred = model.predict(features)
    return y_pred


@app.get('/', response_class=HTMLResponse)
def route_page(request: Request):
    """Home endpoint."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/upload")
async def upload_predict(request: Request, file: UploadFile = File(...)):
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
    output_file = "data/predictions.csv"
    df.to_csv(output_file, index=False)

    logger.info('Returning predictions as csv file: %s', output_file)
    return templates.TemplateResponse("index.html", {"request": request,
                                                     "download_link": "/data/predictions.csv"})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9696)
