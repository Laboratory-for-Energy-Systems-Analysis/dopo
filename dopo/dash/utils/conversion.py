import pandas as pd

def convert_dataframe_to_dict(df: pd.DataFrame) -> dict:
    return df.to_dict()