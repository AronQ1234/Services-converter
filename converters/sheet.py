from pathlib import Path
from fastapi import HTTPException
import pandas as pd

def convert_sheet(ext: str, target_format: str, input_path: Path, output_path: Path) -> None:
    try:
        if ext == '.xlsx' and target_format.lower() == 'csv':
            pd.read_excel(input_path, engine='openpyxl').to_csv(output_path, index=False)
        elif ext == '.xlsx' and target_format.lower() == 'json':
            pd.read_excel(input_path, engine='openpyxl').to_json(output_path, orient='records', indent=2)
        elif ext == '.csv' and target_format.lower() == 'xlsx':
            pd.read_csv(input_path).to_excel(output_path, index=False, engine='openpyxl')
        elif ext == '.csv' and target_format.lower() == 'json':
            pd.read_csv(input_path).to_json(output_path, orient='records', indent=2)
        elif ext == '.json' and target_format.lower() == 'csv':
            pd.read_json(input_path).to_csv(output_path, index=False)
        elif ext == '.json' and target_format.lower() == 'xlsx':
            pd.read_json(input_path).to_excel(output_path, index=False, engine='openpyxl')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sheet conversion failed: {e}")
