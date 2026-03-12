"""
Credit Scoring Model Retraining Pipeline
Main orchestration script for model retraining

Implements: MODEL_RETRAINING_PIPELINE.md
"""

from google.cloud import storage
import pandas as pd
import lightgbm as lgb
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    roc_auc_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix
)
from datetime import datetime
from feature_engineering import engineer_features, validate_features
from email_notifier import send_email_notification
import json
import os
import sys

# Configuration
GCS_BUCKET = os.getenv('GCS_BUCKET', 'credit-scoring-retrain-976448868286')
MIN_SAMPLES = int(os.getenv('MIN_SAMPLES', '500'))
MIN_AUC_IMPROVEMENT = float(os.getenv('MIN_AUC_IMPROVEMENT', '0.02'))
PROMOTION_THRESHOLD = float(os.getenv('PROMOTION_THRESHOLD', '0.86'))


def log(message):
    """Print timestamped log message"""
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}")


def load_latest_export():
    """Load most recent Firestore export from GCS"""
    log("Loading latest data export from GCS")
    
    client = storage.Client()
    bucket = client.bucket(GCS_BUCKET)
    
    # List all exports
    blobs = list(bucket.list_blobs(prefix='data/exports/loan_applications_'))
    if not blobs:
        raise ValueError("No data exports found in GCS")
    
    # Get most recent
    latest_blob = max(blobs, key=lambda b: b.time_created)
    log(f"Found latest export: {latest_blob.name}")
    
    # Download and load
    df = pd.read_parquet(f'gs://{GCS_BUCKET}/{latest_blob.name}')
    log(f"Loaded {len(df)} records from {latest_blob.name}")
    
    return df


def prepare_target(df):
    """
    Create target variable based on data availability
    Options:
    1. Ground truth (actual_default) - preferred
    2. Proxy: approval status - temporary
    """
    if 'actual_default' in df.columns and df['actual_default'].notna().sum() > 100:
        log("Using ground truth labels (actual_default)")
        labeled_df = df[df['actual_default'].notna()].copy()
        log(f"Found {len(labeled_df)} labeled samples")
        return labeled_df
    else:
        log("Ground truth not available. Using proxy: approval status")
        log("  Note: This is for model calibration only, not true retraining")
        # Proxy: rejected applications as "risky" (target=1)
        df = df.copy()
        df['actual_default'] = (~df['approved']).astype(int)
        return df


def train_lightgbm(X_train, y_train, X_val, y_val):
    """
    Train LightGBM with production parameters
    """
    log("Training LightGBM model")
    
    pos_weight = (y_train == 0).sum() / (y_train == 1).sum()
    log(f"Class weight (neg/pos): {pos_weight:.2f}")
    
    params = {
        'objective': 'binary',
        'metric': 'auc',
        'n_estimators': 1000,
        'learning_rate': 0.03,
        'num_leaves': 31,
        'max_depth': 6,
        'min_child_samples': 30,
        'subsample': 0.8,
        'colsample_bytree': 0.8,
        'reg_alpha': 0.1,
        'reg_lambda': 0.1,
        'scale_pos_weight': pos_weight,
        'random_state': 42,
        'n_jobs': -1,
        'verbose': -1
    }
    
    model = lgb.LGBMClassifier(**params)
    model.fit(
        X_train, y_train,
        eval_set=[(X_val, y_val)],
        callbacks=[lgb.early_stopping(50, verbose=False)]
    )
    
    log(f"Training complete. Best iteration: {model.best_iteration_}")
    
    return model


def evaluate_model(model, X_test, y_test, threshold=0.5):
    """Calculate comprehensive metrics"""
    log(f"Evaluating model with threshold={threshold}")
    
    y_proba = model.predict_proba(X_test)[:, 1]
    y_pred = (y_proba >= threshold).astype(int)
    
    metrics = {
        'auc_roc': float(roc_auc_score(y_test, y_proba)),
        'precision': float(precision_score(y_test, y_pred, zero_division=0)),
        'recall': float(recall_score(y_test, y_pred, zero_division=0)),
        'f1_score': float(f1_score(y_test, y_pred, zero_division=0)),
        'threshold': threshold,
        'n_samples': len(y_test),
        'positive_rate': float(y_test.mean()),
    }
    
    log(f"  AUC-ROC:   {metrics['auc_roc']:.4f}")
    log(f"  Precision: {metrics['precision']:.4f}")
    log(f"  Recall:    {metrics['recall']:.4f}")
    log(f"  F1 Score:  {metrics['f1_score']:.4f}")
    
    return metrics


def compare_with_production(new_model, X_test, y_test):
    """
    Compare new model vs current production model
    Only promote if AUC improvement >= threshold
    """
    log("Comparing with production model")
    
    client = storage.Client()
    bucket = client.bucket(GCS_BUCKET)
    
    # Load production model
    try:
        prod_blob = bucket.blob('models/production/lgb_model_optimized.pkl')
        prod_blob.download_to_filename('/tmp/prod_model.pkl')
        prod_model = joblib.load('/tmp/prod_model.pkl')
        log("Production model loaded successfully")
    except Exception as e:
        log(f"Warning: Could not load production model: {e}")
        log("Assuming this is the first model deployment")
        return True, evaluate_model(new_model, X_test, y_test, PROMOTION_THRESHOLD), None
    
    # Evaluate both
    new_metrics = evaluate_model(new_model, X_test, y_test, threshold=PROMOTION_THRESHOLD)
    prod_metrics = evaluate_model(prod_model, X_test, y_test, threshold=PROMOTION_THRESHOLD)
    
    log("="*60)
    log("MODEL COMPARISON")
    log("="*60)
    log(f"Production AUC: {prod_metrics['auc_roc']:.4f}")
    log(f"New Model AUC:  {new_metrics['auc_roc']:.4f}")
    log(f"Improvement:    {(new_metrics['auc_roc'] - prod_metrics['auc_roc']):.4f}")
    log("="*60)
    
    # Decision: promote if improvement >= threshold
    improvement = new_metrics['auc_roc'] - prod_metrics['auc_roc']
    should_promote = improvement >= MIN_AUC_IMPROVEMENT
    
    if should_promote:
        log(f"DECISION: PROMOTE (improvement {improvement:.4f} >= {MIN_AUC_IMPROVEMENT})")
    else:
        log(f"DECISION: DO NOT PROMOTE (improvement {improvement:.4f} < {MIN_AUC_IMPROVEMENT})")
    
    return should_promote, new_metrics, prod_metrics


def save_to_staging(model, metrics, feature_names):
    """Save model and metadata to GCS staging area"""
    log("Saving model to staging")
    
    client = storage.Client()
    bucket = client.bucket(GCS_BUCKET)
    
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    
    # Save model
    local_path = '/tmp/retrained_model.pkl'
    joblib.dump(model, local_path)
    
    model_blob = bucket.blob(f'models/staging/lgb_retrained_{timestamp}.pkl')
    model_blob.upload_from_filename(local_path)
    log(f"Model saved: gs://{GCS_BUCKET}/models/staging/lgb_retrained_{timestamp}.pkl")
    
    # Save metadata
    metadata = {
        'timestamp': timestamp,
        'metrics': metrics,
        'feature_names': feature_names,
        'model_params': model.get_params(),
        'n_features': len(feature_names),
    }
    
    metadata_blob = bucket.blob(f'models/staging/metadata_{timestamp}.json')
    metadata_blob.upload_from_string(json.dumps(metadata, indent=2, default=str))
    log(f"Metadata saved: gs://{GCS_BUCKET}/models/staging/metadata_{timestamp}.json")
    
    return timestamp


def promote_to_production(timestamp):
    """Copy staging model to production"""
    log("Promoting model to production")
    
    client = storage.Client()
    bucket = client.bucket(GCS_BUCKET)
    
    # Archive current production model if exists
    try:
        prod_blob = bucket.blob('models/production/lgb_model_optimized.pkl')
        archive_name = f'models/archive/lgb_model_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.pkl'
        bucket.copy_blob(prod_blob, bucket, archive_name)
        log(f"Current production model archived: {archive_name}")
    except Exception as e:
        log(f"No existing production model to archive: {e}")
    
    # Copy staging to production
    staging_blob = bucket.blob(f'models/staging/lgb_retrained_{timestamp}.pkl')
    bucket.copy_blob(staging_blob, bucket, 'models/production/lgb_model_optimized.pkl')
    log("Model promoted to production!")
    
    # Copy metadata
    metadata_staging = bucket.blob(f'models/staging/metadata_{timestamp}.json')
    bucket.copy_blob(metadata_staging, bucket, 'models/production/metadata_latest.json')
    log("Metadata promoted to production")


def main():
    """Main retraining pipeline"""
    log("="*60)
    log("CREDIT SCORING MODEL RETRAINING PIPELINE")
    log("="*60)
    log(f"Configuration:")
    log(f"  GCS Bucket: {GCS_BUCKET}")
    log(f"  Min Samples: {MIN_SAMPLES}")
    log(f"  Min AUC Improvement: {MIN_AUC_IMPROVEMENT}")
    log(f"  Promotion Threshold: {PROMOTION_THRESHOLD}")
    log("="*60)
    
    try:
        # Step 1: Load data
        df = load_latest_export()
        
        if len(df) < MIN_SAMPLES:
            log(f"ERROR: Not enough data. Need {MIN_SAMPLES}, have {len(df)}.")
            log("Exiting without retraining.")
            sys.exit(0)
        
        # Step 2: Prepare target
        df = prepare_target(df)
        
        # Step 3: Validate and clean data
        log("Validating data quality")
        df_clean, invalid_count = validate_features(df)
        if invalid_count > 0:
            log(f"Removed {invalid_count} invalid records")
        log(f"Clean records: {len(df_clean)}")
        
        # Step 4: Engineer features
        log("Engineering features")
        X = engineer_features(df_clean)
        y = df_clean['actual_default']
        
        log(f"Features engineered: {X.shape[1]} features")
        log(f"Target distribution: Default={y.sum()}, No Default={len(y)-y.sum()}")
        log(f"Default rate: {y.mean()*100:.2f}%")
        
        # Step 5: Split data
        log("Splitting data into train/val/test")
        X_train, X_temp, y_train, y_temp = train_test_split(
            X, y, test_size=0.3, stratify=y, random_state=42
        )
        X_val, X_test, y_val, y_test = train_test_split(
            X_temp, y_temp, test_size=0.5, stratify=y_temp, random_state=42
        )
        
        log(f"Train: {X_train.shape[0]} samples")
        log(f"Val:   {X_val.shape[0]} samples")
        log(f"Test:  {X_test.shape[0]} samples")
        
        # Step 6: Train model
        new_model = train_lightgbm(X_train, y_train, X_val, y_val)
        
        # Step 7: Evaluate and compare
        should_promote, new_metrics, prod_metrics = compare_with_production(
            new_model, X_test, y_test
        )
        
        # Step 8: Save to staging
        timestamp = save_to_staging(new_model, new_metrics, X.columns.tolist())
        
        # Step 9: Promote if better
        if should_promote:
            promote_to_production(timestamp)
            log("\n" + "="*60)
            log("SUCCESS: NEW MODEL DEPLOYED TO PRODUCTION")
            log("="*60)
        else:
            log("\n" + "="*60)
            log("INFO: New model did not meet promotion criteria")
            log("Model saved to staging for manual review")
            log("="*60)
        
        # Step 10: Send email notification
        log("\nSending email notification...")
        try:
            subject = f"{'✅ Model Promoted' if should_promote else '⚠️ Model Not Promoted'} - Credit Scoring Retraining"
            send_email_notification(
                subject=subject,
                metrics=new_metrics,
                prod_metrics=prod_metrics,
                promoted=should_promote,
                timestamp=timestamp
            )
            log("✓ Email notification sent")
        except Exception as e:
            log(f"WARNING: Failed to send email notification: {e}")
        
        log("\nRetraining complete")
        log(f"Timestamp: {timestamp}")
        
    except Exception as e:
        log(f"ERROR: Retraining failed: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Send failure notification
        try:
            send_email_notification(
                subject="❌ Model Retraining Failed - Credit Scoring",
                metrics={'error': str(e)},
                prod_metrics=None,
                promoted=False,
                timestamp=datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            )
        except:
            pass  # Don't fail if notification fails
        
        sys.exit(1)


if __name__ == "__main__":
    main()
