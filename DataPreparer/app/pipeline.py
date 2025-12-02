import pandas as pd
from sklearn.preprocessing import StandardScaler, MinMaxScaler

def apply_pipeline(df, pipeline):
    for step in pipeline["steps"]:

        if step["name"] == "imputation":
            if step["strategy"] == "mean":
                df = df.fillna(df.mean())

        if step["name"] == "one_hot_encoding":
            df = pd.get_dummies(df, columns=step["columns"])

        if step["name"] == "scaling":
            scaler = StandardScaler() if step["method"] == "standard" else MinMaxScaler()
            numeric_cols = df.select_dtypes(include=["float64", "int64"]).columns
            df[numeric_cols] = scaler.fit_transform(df[numeric_cols])

    return df
