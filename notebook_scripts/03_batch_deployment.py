#!/usr/bin/env python
# coding: utf-8

from mlops.project_libraries import argparse, os, pd, mlflow
from mlops.util_funcs import scrub_data

parser = argparse.ArgumentParser()

parser.add_argument('--input_data_path', required=True,
                    help='path to the csv file containing the data')
parser.add_argument('--experiment_id', required=True,
                    help='id of the experiment')  # 6 for this example
parser.add_argument('--run_id', required=True,
                    help='id of the run')  # 45a3990ff1e140afbe48334a8422bec7
parser.add_argument('--output_data_path', required=True,
                    help='path to save the predictions')


args = parser.parse_args()
input_data_path = args.input_data_path
experiment_id = args.experiment_id
run_id = args.run_id
output_data_path = args.output_data_path

# fill in AWS profile
os.environ["AWS_PROFILE"] = "demiga-g"


# Setting tracking uri (unique resource identifier)
TRACKING_SERVER_HOST = '127.0.0.1'  # '16.171.136.194'
mlflow.set_tracking_uri(f"http://{TRACKING_SERVER_HOST}:5000")


def load_model():
    """Load a model from an experiment run."""
    base_location = 'mlflow-artifacts:'  # 's3://midega-mlflow-artifacts'
    logged_model = f"{base_location}/{experiment_id}/{run_id}/artifacts/model"
    return mlflow.pyfunc.load_model(logged_model)


# def save_results(new_data, y_pred):
#     """save the results in a new dataframe"""
#     df_result = pd.DataFrame()
#     df_result['ID'] = new_data['ID']
#     df_result['PredictedResponse'] = y_pred
#     return df_result.to_csv(output_data_path, index=False)


def apply_model():
    """Load data, apply model, and give predictions."""
    new_data = pd.read_csv(input_data_path)
    df = scrub_data(new_data).to_dict(orient='records')
    model = load_model()
    y_pred = model.predict(df)
    return new_data['ID'], y_pred


def save_results():
    # save prediction to new dataset
    customer_ids, y_pred = apply_model()
    df_result = pd.DataFrame()
    df_result['ID'] = customer_ids
    df_result['PredictedResponse'] = y_pred
    return df_result.to_csv(output_data_path, index=False)
        
    
if __name__ == '__main__':
    save_results()