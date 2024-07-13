import mlflow
import numpy as np
import pandas as pd
from datetime import datetime
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import PowerTransformer
from sklearn.metrics import (f1_score, precision_score, recall_score, 
                             roc_auc_score, accuracy_score)

# Create the necessary variables
dependants = ['Kidhome', 'Teenhome']

# assuming analysis was conducted in 2014 
now = 2014

# Define the bin edges
bins = [18, 28, 38, 48, 58, 65, np.inf]

# Define the labels for each age group
labels = ['18-27', '28-37', '38-47', '48-57', '58-65', '65+']

# End of financial year
end_fiscal = datetime(2014, 6, 30)

# Redundant features
red_ftrs_1 = ["ID", "Year_Birth", "Dt_Customer", "Z_CostContact", "Z_Revenue", "Response", 'Age']

# List of categorical and numeric features
categ_ftrs_1 = ['Education', 'Marital_Status', 'Kidhome', 'Teenhome', 'AcceptedCmp3', 'AcceptedCmp4', 
                'AcceptedCmp5', 'AcceptedCmp1', 'AcceptedCmp2', 'Complain', 'Age_Group']

num_ftrs_1 = ['Income', 'Recency', 'MntWines', 'MntFruits', 'MntMeatProducts', 'MntFishProducts', 
              'MntSweetProducts', 'MntGoldProds', 'NumDealsPurchases', 'NumWebPurchases', 
              'NumCatalogPurchases', 'NumStorePurchases', 'NumWebVisitsMonth', 'Onboard_Days']

# Function to do data cleaning and feature preprocessing
def scrub_data(df):
    
    # Convert 'Kidhome' and 'Teenhome' to categorical
    # but first fillna with the most frequent value
    df[dependants] = df[dependants].fillna(df[dependants].mode().iloc[0])
    df[dependants] = df[dependants].applymap(lambda x: 1 if x > 0 else 0)
    
    # Conversions into 'datetime' data type
    # but first fillna in both variables
    df['Year_Birth'] = df['Year_Birth'].fillna(int(df['Year_Birth'].median()))
    df['Year_Birth'] = pd.to_datetime(df['Year_Birth'], format='%Y')
    
    df['Dt_Customer'] = df['Dt_Customer'].fillna(df['Dt_Customer'].mode().iloc[0])
    df["Dt_Customer"] = pd.to_datetime(df["Dt_Customer"])
    
    # Calculate age
    df['Age'] = now - df['Year_Birth'].dt.year
    
    # Create age group feature
    df['Age_Group'] = pd.cut(df['Age'], bins=bins, labels=labels, right=False)
    
    # Calculate the number of days since customer enrolled
    df['Onboard_Days'] = (end_fiscal - df['Dt_Customer']).dt.days
    
    # Droping redundant features
    existing_red_ftrs = [col for col in red_ftrs_1 if col in df.columns]
    df = df.drop(existing_red_ftrs, axis=1)
    
    # handle missing values and scale numeric data
    num_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('normalize', PowerTransformer(method='yeo-johnson')),
    ])
    
    ct = ColumnTransformer([
        ('num_trans', num_transformer, num_ftrs_1),
        ('cat_trans', SimpleImputer(strategy='most_frequent'), categ_ftrs_1)
    ])
        
    df = pd.DataFrame(ct.fit_transform(df), 
                      columns=num_ftrs_1 + categ_ftrs_1)
    
    # Ensure that the final df features are in the right data types
    df[categ_ftrs_1] = df[categ_ftrs_1].astype('str')
    df[num_ftrs_1] = df[num_ftrs_1].astype('float')
     
    return df


# calculate and log the evaluation metrics
def eval_metrics_logs(y_val, y_pred):
    
    # calcualte the evaluation metrics
    metrics = {
        'f1': f1_score(y_val, y_pred.round()), 
        'precision': precision_score(y_val, y_pred.round(), zero_division=0),
        'recall': recall_score(y_val, y_pred.round()),
        'pr_auc': roc_auc_score(y_val, y_pred.round()),
        'accuracy': accuracy_score(y_val, y_pred.round())
    }
    
    # log the evaluation metrics
    mlflow.log_metrics(metrics)
    
    # check the precision score
    return metrics['precision']