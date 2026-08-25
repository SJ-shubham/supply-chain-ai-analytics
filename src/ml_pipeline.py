import os
import pandas as pd
import numpy as np
import joblib
from typing import Dict, Any, Tuple, List

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score, RandomizedSearchCV
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import (accuracy_score, precision_score, recall_score, f1_score,
                             roc_auc_score, confusion_matrix, classification_report,
                             mean_absolute_error, mean_squared_error, r2_score)
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

try:
    from xgboost import XGBClassifier, XGBRegressor
    HAS_XGBOOST = True
except ImportError:
    HAS_XGBOOST = False
    print("[Warning] xgboost not installed. XGBoost models will be skipped.")

MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")
os.makedirs(MODELS_DIR, exist_ok=True)

# ========================================================================================
#  CLASSIFICATION PIPELINE -- Late Delivery Risk Prediction
# ========================================================================================

CLASSIFICATION_CAT_FEATURES = ['Shipping Mode', 'Market', 'Order Region', 'Category Name', 'Customer Segment', 'Department Name']
CLASSIFICATION_NUM_FEATURES = ['Order Item Quantity', 'Sales', 'Order Item Discount Rate', 'Order Item Product Price',
                               'Days for shipment (scheduled)', 'Regional_Late_Rate', 'Shipping_Mode_Late_Rate']
CLASSIFICATION_TARGET = 'Late_delivery_risk'


def build_preprocessor(cat_features: List[str], num_features: List[str]) -> ColumnTransformer:
    """Build a ColumnTransformer preprocessing pipeline."""
    num_pipeline = Pipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])
    cat_pipeline = Pipeline([
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('encoder', OneHotEncoder(handle_unknown='ignore', drop='first', sparse_output=False))
    ])
    preprocessor = ColumnTransformer([
        ('num', num_pipeline, num_features),
        ('cat', cat_pipeline, cat_features)
    ], remainder='drop')
    return preprocessor


def train_classification_pipeline(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Full classification pipeline: split -> preprocess -> train 3 models -> CV -> tune XGBoost -> evaluate -> export.
    """
    print("=" * 60)
    print("  MODULE 5: CLASSIFICATION -- Late Delivery Risk Prediction")
    print("=" * 60)

    # --- Feature Enhancement ---
    df_copy = df.copy()
    if 'Order_Date' in df_copy.columns:
        dt = pd.to_datetime(df_copy['Order_Date'])
        df_copy['order_month'] = dt.dt.month
        df_copy['order_dayofweek'] = dt.dt.dayofweek
        df_copy['order_hour'] = dt.dt.hour
    if 'Regional_Late_Rate' in df_copy.columns and 'Shipping_Mode_Late_Rate' in df_copy.columns:
        df_copy['late_risk_interaction'] = df_copy['Regional_Late_Rate'] * df_copy['Shipping_Mode_Late_Rate']

    num_feats = CLASSIFICATION_NUM_FEATURES.copy()
    for col in ['order_month', 'order_dayofweek', 'order_hour', 'late_risk_interaction']:
        if col in df_copy.columns and col not in num_feats:
            num_feats.append(col)

    # --- Step 1: Feature/Target Separation ---
    available_cat = [c for c in CLASSIFICATION_CAT_FEATURES if c in df_copy.columns]
    available_num = [c for c in num_feats if c in df_copy.columns]
    X = df_copy[available_cat + available_num].copy()
    y = df_copy[CLASSIFICATION_TARGET].copy()
    print(f"\n[Step 1] Features: {len(available_cat)} categorical + {len(available_num)} numerical = {X.shape[1]} total")
    print(f"[Step 1] Target distribution:\n{y.value_counts().to_string()}")

    # --- Step 2: Train-Test Split (80/20 stratified) ---
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42, stratify=y)
    print(f"\n[Step 2] Train set: {X_train.shape[0]:,} rows | Test set: {X_test.shape[0]:,} rows")

    # --- Step 3: Build Preprocessor ---
    preprocessor = build_preprocessor(available_cat, available_num)
    X_train_processed = preprocessor.fit_transform(X_train)
    X_test_processed = preprocessor.transform(X_test)
    print(f"[Step 3] Preprocessed feature dimensions: {X_train_processed.shape[1]} columns after encoding")

    # --- Step 4: Define Models ---
    models = {
        'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42),
        'Random Forest': RandomForestClassifier(n_estimators=50, max_depth=10, random_state=42, n_jobs=-1),
    }
    if HAS_XGBOOST:
        models['XGBoost'] = XGBClassifier(n_estimators=100, max_depth=5, learning_rate=0.1,
                                          subsample=0.8, colsample_bytree=0.8,
                                          random_state=42, eval_metric='logloss',
                                          n_jobs=-1)

    # --- Step 5: 5-Fold Stratified Cross-Validation ---
    print(f"\n[Step 5] Running 5-Fold Stratified Cross-Validation on training set...")
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_results = {}
    for name, model in models.items():
        scores = cross_val_score(model, X_train_processed, y_train, cv=cv, scoring='accuracy', n_jobs=-1)
        cv_results[name] = {'cv_mean': round(scores.mean(), 4), 'cv_std': round(scores.std(), 4)}
        print(f"  - {name}: CV Accuracy = {scores.mean():.4f} +- {scores.std():.4f}")

    # --- Step 6: Train all models on full training set & evaluate on test set ---
    print(f"\n[Step 6] Training all models on full training set and evaluating on held-out test set...")
    results_table = []
    trained_models = {}

    for name, model in models.items():
        model.fit(X_train_processed, y_train)
        y_pred = model.predict(X_test_processed)
        y_proba = model.predict_proba(X_test_processed)[:, 1] if hasattr(model, 'predict_proba') else None

        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, zero_division=0)
        rec = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        roc = roc_auc_score(y_test, y_proba) if y_proba is not None else 0.0
        cm = confusion_matrix(y_test, y_pred)

        results_table.append({
            'Model': name,
            'Accuracy': round(acc, 4),
            'Precision': round(prec, 4),
            'Recall': round(rec, 4),
            'F1_Score': round(f1, 4),
            'ROC_AUC': round(roc, 4),
            'CV_Mean_Acc': cv_results[name]['cv_mean'],
            'CV_Std': cv_results[name]['cv_std']
        })
        trained_models[name] = {'model': model, 'predictions': y_pred, 'probabilities': y_proba, 'confusion_matrix': cm}
        print(f"  - {name}: Acc={acc:.4f} | Prec={prec:.4f} | Rec={rec:.4f} | F1={f1:.4f} | AUC={roc:.4f}")

    results_df = pd.DataFrame(results_table)

    # --- Step 7: Select Best Model by F1-Score ---
    best_row = results_df.loc[results_df['F1_Score'].idxmax()]
    best_model_name = best_row['Model']
    best_model = trained_models[best_model_name]['model']
    print(f"\n[Step 7] >>> BEST MODEL SELECTED: {best_model_name} (F1={best_row['F1_Score']}, AUC={best_row['ROC_AUC']})")

    # --- Step 8: Hyperparameter Tuning (XGBoost if it's the best, otherwise skip) ---
    if best_model_name == 'XGBoost' and HAS_XGBOOST:
        print(f"\n[Step 8] Running RandomizedSearchCV hyperparameter tuning on XGBoost...")
        param_grid = {
            'n_estimators': [200, 300, 500],
            'max_depth': [4, 6, 8],
            'learning_rate': [0.05, 0.1, 0.2],
            'subsample': [0.7, 0.8, 0.9],
            'colsample_bytree': [0.7, 0.8, 0.9],
            'min_child_weight': [1, 3, 5]
        }
        search = RandomizedSearchCV(
            XGBClassifier(random_state=42, eval_metric='logloss', n_jobs=-1),
            param_distributions=param_grid,
            n_iter=5, scoring='f1', cv=3, random_state=42, n_jobs=-1, verbose=0
        )
        search.fit(X_train_processed, y_train)
        best_model = search.best_estimator_
        print(f"  - Best Params: {search.best_params_}")
        print(f"  - Best CV F1: {search.best_score_:.4f}")

        # Re-evaluate tuned model on test set
        y_pred_tuned = best_model.predict(X_test_processed)
        y_proba_tuned = best_model.predict_proba(X_test_processed)[:, 1]
        f1_tuned = f1_score(y_test, y_pred_tuned)
        auc_tuned = roc_auc_score(y_test, y_proba_tuned)
        print(f"  - Tuned XGBoost Test Performance: F1={f1_tuned:.4f}, AUC={auc_tuned:.4f}")
        trained_models[best_model_name]['model'] = best_model
        trained_models[best_model_name]['predictions'] = y_pred_tuned
        trained_models[best_model_name]['probabilities'] = y_proba_tuned
        trained_models[best_model_name]['confusion_matrix'] = confusion_matrix(y_test, y_pred_tuned)
    else:
        print(f"\n[Step 8] Skipping tuning (best model is {best_model_name}).")

    # --- Step 9: Export Model & Preprocessor ---
    clf_model_path = os.path.join(MODELS_DIR, "late_delivery_xgboost.pkl")
    clf_prep_path = os.path.join(MODELS_DIR, "classification_preprocessor.pkl")
    joblib.dump(best_model, clf_model_path)
    joblib.dump(preprocessor, clf_prep_path)
    print(f"\n[Step 9] Exported: {clf_model_path}")
    print(f"[Step 9] Exported: {clf_prep_path}")

    print("=" * 60 + "\n")
    return {
        'results_df': results_df,
        'best_model_name': best_model_name,
        'best_model': best_model,
        'trained_models': trained_models,
        'preprocessor': preprocessor,
        'y_test': y_test,
        'X_test_processed': X_test_processed,
        'feature_names': available_cat + available_num
    }


# ========================================================================================
#  REGRESSION PIPELINE -- Delivery Duration Prediction
# ========================================================================================

REGRESSION_CAT_FEATURES = ['Shipping Mode', 'Market', 'Order Region', 'Category Name']
REGRESSION_NUM_FEATURES = ['Days for shipment (scheduled)', 'Order Item Quantity', 'Sales', 'Regional_Late_Rate']
REGRESSION_TARGET = 'Days for shipping (real)'


def train_regression_pipeline(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Full regression pipeline: split -> preprocess -> train 3 models -> CV -> tune -> evaluate -> export.
    """
    print("=" * 60)
    print("  MODULE 6: REGRESSION -- Delivery Duration Prediction")
    print("=" * 60)

    available_cat = [c for c in REGRESSION_CAT_FEATURES if c in df.columns]
    available_num = [c for c in REGRESSION_NUM_FEATURES if c in df.columns]
    X = df[available_cat + available_num].copy()
    y = df[REGRESSION_TARGET].copy()
    print(f"\n[Step 1] Features: {len(available_cat)} cat + {len(available_num)} num = {X.shape[1]} total")

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42)
    print(f"[Step 2] Train: {X_train.shape[0]:,} | Test: {X_test.shape[0]:,}")

    preprocessor = build_preprocessor(available_cat, available_num)
    X_train_p = preprocessor.fit_transform(X_train)
    X_test_p = preprocessor.transform(X_test)

    models = {
        'Linear Regression': LinearRegression(),
        'Random Forest Regressor': RandomForestRegressor(n_estimators=50, max_depth=10, random_state=42, n_jobs=-1),
    }
    if HAS_XGBOOST:
        models['XGBoost Regressor'] = XGBRegressor(n_estimators=100, max_depth=5, learning_rate=0.1,
                                                    subsample=0.8, random_state=42, n_jobs=-1)

    print(f"\n[Step 5] 5-Fold Cross-Validation (MAE)...")
    cv_results = {}
    for name, model in models.items():
        scores = cross_val_score(model, X_train_p, y_train, cv=5, scoring='neg_mean_absolute_error', n_jobs=-1)
        mae_scores = -scores
        cv_results[name] = {'cv_mean_mae': round(mae_scores.mean(), 4), 'cv_std': round(mae_scores.std(), 4)}
        print(f"  - {name}: CV MAE = {mae_scores.mean():.4f} +- {mae_scores.std():.4f}")

    print(f"\n[Step 6] Training and evaluating on test set...")
    results_table = []
    trained_models = {}
    for name, model in models.items():
        model.fit(X_train_p, y_train)
        y_pred = model.predict(X_test_p)
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)
        results_table.append({
            'Model': name, 'MAE': round(mae, 4), 'RMSE': round(rmse, 4), 'R2_Score': round(r2, 4),
            'CV_Mean_MAE': cv_results[name]['cv_mean_mae'], 'CV_Std': cv_results[name]['cv_std']
        })
        trained_models[name] = {'model': model, 'predictions': y_pred}
        print(f"  - {name}: MAE={mae:.4f} | RMSE={rmse:.4f} | R2={r2:.4f}")

    results_df = pd.DataFrame(results_table)
    best_row = results_df.loc[results_df['R2_Score'].idxmax()]
    best_model_name = best_row['Model']
    best_model = trained_models[best_model_name]['model']
    print(f"\n[Step 7] >>> BEST REGRESSOR: {best_model_name} (R2={best_row['R2_Score']}, MAE={best_row['MAE']})")

    reg_model_path = os.path.join(MODELS_DIR, "delivery_time_regressor.pkl")
    reg_prep_path = os.path.join(MODELS_DIR, "regression_preprocessor.pkl")
    joblib.dump(best_model, reg_model_path)
    joblib.dump(preprocessor, reg_prep_path)
    print(f"\n[Step 9] Exported: {reg_model_path}")
    print(f"[Step 9] Exported: {reg_prep_path}")
    print("=" * 60 + "\n")

    return {
        'results_df': results_df, 'best_model_name': best_model_name, 'best_model': best_model,
        'trained_models': trained_models, 'preprocessor': preprocessor,
        'y_test': y_test, 'y_pred_best': trained_models[best_model_name]['predictions']
    }


# ========================================================================================
#  CLUSTERING PIPELINE -- Customer Segmentation (K-Means)
# ========================================================================================

CLUSTER_FEATURES = ['Customer_Recency', 'Customer_Frequency', 'Customer_Monetary', 'Customer_AOV', 'Customer_Profit']


def train_clustering_pipeline(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Full K-Means clustering pipeline: aggregate -> scale -> elbow -> silhouette -> fit -> profile -> export.
    """
    print("=" * 60)
    print("  MODULE 7: CLUSTERING -- Customer Segmentation (K-Means)")
    print("=" * 60)

    available_feats = [c for c in CLUSTER_FEATURES if c in df.columns]
    customer_df = df.groupby('Customer Id')[available_feats].first().reset_index()
    print(f"\n[Step 1] Unique customers: {customer_df.shape[0]:,} | Features: {available_feats}")

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(customer_df[available_feats])
    print(f"[Step 2] Scaled feature matrix: {X_scaled.shape}")

    # Elbow Method (WCSS)
    print(f"\n[Step 3] Elbow Method (WCSS) for k in [2, 8]...")
    k_range = range(2, 9)
    wcss_scores = []
    for k in k_range:
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        km.fit(X_scaled)
        wcss_scores.append(km.inertia_)
        print(f"  - k={k}: WCSS = {km.inertia_:,.2f}")

    # Silhouette Score
    print(f"\n[Step 4] Silhouette Score Analysis for k in [2, 8]...")
    sil_scores = []
    for k in k_range:
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = km.fit_predict(X_scaled)
        sil = silhouette_score(X_scaled, labels)
        sil_scores.append(sil)
        print(f"  - k={k}: Silhouette = {sil:.4f}")

    # Select optimal k
    optimal_k = list(k_range)[np.argmax(sil_scores)]
    print(f"\n[Step 5] >>> Optimal k = {optimal_k} (Silhouette = {max(sil_scores):.4f})")

    # Final K-Means fit
    kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
    customer_df['Cluster'] = kmeans.fit_predict(X_scaled)

    # Cluster profiling
    print(f"\n[Step 6] Cluster Persona Profiling:")
    profile = customer_df.groupby('Cluster')[available_feats].mean().round(2)
    print(profile.to_string())

    # Export
    km_model_path = os.path.join(MODELS_DIR, "customer_kmeans_model.pkl")
    km_scaler_path = os.path.join(MODELS_DIR, "kmeans_scaler.pkl")
    joblib.dump(kmeans, km_model_path)
    joblib.dump(scaler, km_scaler_path)
    print(f"\n[Step 7] Exported: {km_model_path}")
    print(f"[Step 7] Exported: {km_scaler_path}")
    print("=" * 60 + "\n")

    return {
        'customer_df': customer_df, 'optimal_k': optimal_k,
        'kmeans': kmeans, 'scaler': scaler, 'profile': profile,
        'wcss_scores': wcss_scores, 'sil_scores': sil_scores, 'k_range': list(k_range)
    }


# ========================================================================================
#  INFERENCE HELPERS (For Web App APIs -- Phase 8)
# ========================================================================================

def predict_late_delivery_risk(order_data: dict) -> dict:
    """Load saved model and predict late delivery risk for a single order."""
    model = joblib.load(os.path.join(MODELS_DIR, "late_delivery_xgboost.pkl"))
    preprocessor = joblib.load(os.path.join(MODELS_DIR, "classification_preprocessor.pkl"))
    input_df = pd.DataFrame([order_data])
    X_processed = preprocessor.transform(input_df)
    proba = model.predict_proba(X_processed)[0][1]
    return {
        "late_probability": round(float(proba), 4),
        "risk_level": "HIGH RISK" if proba >= 0.5 else "LOW RISK"
    }


def predict_shipping_duration(shipment_data: dict) -> dict:
    """Load saved model and predict shipping duration for a single shipment."""
    model = joblib.load(os.path.join(MODELS_DIR, "delivery_time_regressor.pkl"))
    preprocessor = joblib.load(os.path.join(MODELS_DIR, "regression_preprocessor.pkl"))
    input_df = pd.DataFrame([shipment_data])
    X_processed = preprocessor.transform(input_df)
    predicted_days = model.predict(X_processed)[0]
    return {"predicted_days": round(float(predicted_days), 2)}


def predict_customer_segment(rfm_data: dict) -> dict:
    """Load saved model and predict customer segment for given RFM values."""
    kmeans = joblib.load(os.path.join(MODELS_DIR, "customer_kmeans_model.pkl"))
    scaler = joblib.load(os.path.join(MODELS_DIR, "kmeans_scaler.pkl"))
    input_arr = np.array([[rfm_data.get(f, 0) for f in CLUSTER_FEATURES]])
    X_scaled = scaler.transform(input_arr)
    cluster = int(kmeans.predict(X_scaled)[0])
    return {"cluster_id": cluster}
