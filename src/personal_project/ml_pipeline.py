from pathlib import Path
import re
import joblib
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score

DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "Cars Datasets 2025.csv"
MODEL_OUT = Path(__file__).resolve().parents[2] / "models"
MODEL_OUT.mkdir(parents=True, exist_ok=True)


def parse_price(s: str):
    if not isinstance(s, str):
        return np.nan
    s = s.replace(',', '').strip()
    s = re.sub(r"[^0-9\-\.\s]", "", s)
    if '-' in s:
        parts = [p for p in s.split('-') if p.strip() != ""]
        try:
            nums = [float(p) for p in parts]
            return sum(nums) / len(nums)
        except Exception:
            return np.nan
    try:
        return float(s)
    except Exception:
        return np.nan


def extract_number(s: str):
    if not isinstance(s, str):
        return np.nan
    s = s.replace(',', '')
    m = re.findall(r"[-+]?[0-9]*\.?[0-9]+", s)
    if not m:
        return np.nan
    nums = [float(x) for x in m]
    return sum(nums) / len(nums)


def load_and_clean(path=DATA_PATH):
    df = pd.read_csv(path, encoding='latin1')
    df.columns = [c.strip() for c in df.columns]

    df['price_raw'] = df.get('Cars Prices', '')
    df['price'] = df['price_raw'].apply(parse_price)

    df['horsepower'] = df.get('HorsePower', '').apply(extract_number)
    df['cc'] = df.get('CC/Battery Capacity', '').apply(extract_number)
    df['perf_sec'] = df.get('Performance(0 - 100 )KM/H', '').apply(extract_number)
    df['torque'] = df.get('Torque', '').apply(extract_number)
    df['seats'] = pd.to_numeric(df.get('Seats', ''), errors='coerce')

    features = ['Company Names', 'Cars Names', 'horsepower', 'cc', 'perf_sec', 'torque', 'seats', 'Fuel Types']
    df_model = df[[*features, 'price']].copy()
    df_model = df_model.dropna(subset=['price'])
    return df_model


def train():
    df = load_and_clean()
    if df.shape[0] < 10:
        raise RuntimeError('Not enough rows to train')

    X = df.drop(columns=['price'])
    y = df['price'].astype(float)

    numeric_cols = ['horsepower', 'cc', 'perf_sec', 'torque', 'seats']
    cat_cols = ['Company Names', 'Fuel Types']

    num_transform = make_pipeline(SimpleImputer(strategy='median'), StandardScaler())
    cat_transform = make_pipeline(SimpleImputer(strategy='constant', fill_value='missing'), OneHotEncoder(handle_unknown='ignore'))

    preprocessor = ColumnTransformer([
        ('num', num_transform, numeric_cols),
        ('cat', cat_transform, cat_cols),
    ])

    model = make_pipeline(preprocessor, RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1))

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    print('Running quick CV (3 folds) on training set...')
    cv_scores = cross_val_score(model, X_train, y_train, cv=3, scoring='neg_root_mean_squared_error', n_jobs=1)
    print('CV RMSE:', -cv_scores.mean(), '±', cv_scores.std())

    print('Fitting model on full training set...')
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test, preds))
    r2 = r2_score(y_test, preds)
    print(f'Test RMSE: {rmse:.2f}')
    print(f'Test R^2: {r2:.3f}')

    model_file = MODEL_OUT / 'car_price_rf.pkl'
    joblib.dump(model, model_file)
    print('Saved model to', model_file)


if __name__ == '__main__':
    train()
