"""
Pipeline Configuration
Centralized settings for retraining pipeline
"""

import os


class PipelineConfig:
    """Retraining pipeline configuration"""
    
    # GCS Configuration
    GCS_BUCKET = os.getenv('GCS_BUCKET', 'credit-scoring-retrain-513943636250')
    GCS_DATA_PREFIX = 'data/exports'
    GCS_MODEL_STAGING = 'models/staging'
    GCS_MODEL_PRODUCTION = 'models/production'
    GCS_MODEL_ARCHIVE = 'models/archive'
    
    # Data Requirements
    MIN_SAMPLES = int(os.getenv('MIN_SAMPLES', '500'))
    MIN_LABELED_SAMPLES = int(os.getenv('MIN_LABELED_SAMPLES', '100'))
    
    # Model Training
    RANDOM_SEED = 42
    TEST_SIZE = 0.3
    VAL_SIZE = 0.5  # 0.5 of test_size = 15% of total
    
    # Model Evaluation
    PROMOTION_THRESHOLD = float(os.getenv('PROMOTION_THRESHOLD', '0.86'))
    MIN_AUC_IMPROVEMENT = float(os.getenv('MIN_AUC_IMPROVEMENT', '0.02'))
    MIN_AUC_ABSOLUTE = float(os.getenv('MIN_AUC_ABSOLUTE', '0.70'))
    
    # LightGBM Hyperparameters
    LGBM_PARAMS = {
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
        'random_state': RANDOM_SEED,
        'n_jobs': -1,
        'verbose': -1
    }
    
    # Early stopping
    EARLY_STOPPING_ROUNDS = 50
    
    @classmethod
    def display(cls):
        """Display current configuration"""
        print("Pipeline Configuration:")
        print(f"  GCS Bucket: {cls.GCS_BUCKET}")
        print(f"  Min Samples: {cls.MIN_SAMPLES}")
        print(f"  Min Labeled Samples: {cls.MIN_LABELED_SAMPLES}")
        print(f"  Min AUC Improvement: {cls.MIN_AUC_IMPROVEMENT}")
        print(f"  Min AUC Absolute: {cls.MIN_AUC_ABSOLUTE}")
        print(f"  Promotion Threshold: {cls.PROMOTION_THRESHOLD}")
        print(f"  Random Seed: {cls.RANDOM_SEED}")


config = PipelineConfig()
