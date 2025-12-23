import pandas as pd
from sklearn.preprocessing import StandardScaler, MinMaxScaler, LabelEncoder
from typing import Dict, Any

def apply_pipeline(df: pd.DataFrame, pipeline: Dict[str, Any]) -> pd.DataFrame:
    """
    Appliquer un pipeline de transformations sur un DataFrame
    
    Args:
        df: DataFrame pandas à transformer
        pipeline: Dictionnaire contenant les étapes de transformation
    
    Returns:
        DataFrame transformé
    """
    df = df.copy()
    
    steps = pipeline.get("steps", [])
    
    for step in steps:
        step_name = step.get("name", "").lower()
        
        # Imputation des valeurs manquantes
        if step_name == "imputation":
            strategy = step.get("strategy", "mean").lower()
            columns = step.get("columns")
            
            if columns:
                # Colonnes spécifiques
                cols_to_impute = [col for col in columns if col in df.columns]
            else:
                # Toutes les colonnes numériques
                cols_to_impute = df.select_dtypes(include=["float64", "int64"]).columns.tolist()
            
            if strategy == "mean":
                for col in cols_to_impute:
                    df[col] = df[col].fillna(df[col].mean())
            elif strategy == "median":
                for col in cols_to_impute:
                    df[col] = df[col].fillna(df[col].median())
            elif strategy == "mode":
                for col in cols_to_impute:
                    df[col] = df[col].fillna(df[col].mode()[0] if not df[col].mode().empty else 0)
            elif strategy == "forward_fill":
                df[cols_to_impute] = df[cols_to_impute].fillna(method="ffill")
            elif strategy == "backward_fill":
                df[cols_to_impute] = df[cols_to_impute].fillna(method="bfill")
            elif strategy == "drop":
                df = df.dropna(subset=cols_to_impute)
        
        # One-hot encoding
        elif step_name == "one_hot_encoding":
            columns = step.get("columns", [])
            if columns:
                cols_to_encode = [col for col in columns if col in df.columns]
                df = pd.get_dummies(df, columns=cols_to_encode, prefix=cols_to_encode)
        
        # Label encoding
        elif step_name == "label_encoding":
            columns = step.get("columns", [])
            if columns:
                le = LabelEncoder()
                for col in columns:
                    if col in df.columns and df[col].dtype == "object":
                        df[col] = le.fit_transform(df[col].astype(str))
        
        # Scaling/Normalisation
        elif step_name == "scaling":
            method = step.get("method", "standard").lower()
            columns = step.get("columns")
            
            if columns:
                numeric_cols = [col for col in columns if col in df.columns]
            else:
                numeric_cols = df.select_dtypes(include=["float64", "int64"]).columns.tolist()
            
            if numeric_cols:
                if method == "standard":
                    scaler = StandardScaler()
                elif method == "minmax":
                    scaler = MinMaxScaler()
                else:
                    scaler = StandardScaler()
                
                df[numeric_cols] = scaler.fit_transform(df[numeric_cols])
        
        # Suppression de colonnes
        elif step_name == "drop_columns":
            columns = step.get("columns", [])
            cols_to_drop = [col for col in columns if col in df.columns]
            df = df.drop(columns=cols_to_drop)
        
        # Renommage de colonnes
        elif step_name == "rename_columns":
            mapping = step.get("mapping", {})
            df = df.rename(columns=mapping)
        
        # Filtrage des lignes
        elif step_name == "filter_rows":
            condition = step.get("condition")
            if condition:
                # Condition simple: {"column": "age", "operator": ">", "value": 18}
                column = condition.get("column")
                operator = condition.get("operator")
                value = condition.get("value")
                
                if column and column in df.columns:
                    if operator == ">":
                        df = df[df[column] > value]
                    elif operator == ">=":
                        df = df[df[column] >= value]
                    elif operator == "<":
                        df = df[df[column] < value]
                    elif operator == "<=":
                        df = df[df[column] <= value]
                    elif operator == "==":
                        df = df[df[column] == value]
                    elif operator == "!=":
                        df = df[df[column] != value]
    
    return df
