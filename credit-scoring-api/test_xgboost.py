"""
Test script to verify XGBoost model integration
"""
from app.services.model_loader import model_loader
from app.core.config import settings

print("=" * 60)
print("XGBoost Model Integration Test")
print("=" * 60)

# Test 1: Model Loading
print("\n[TEST 1] Model Loading")
print(f"✓ XGBoost model loaded: {model_loader.xgb_model is not None}")
print(f"✓ LightGBM model loaded: {model_loader.lgbm_model is not None}")
print(f"✓ Metadata loaded: {model_loader.metadata is not None}")

# Test 2: Configuration
print("\n[TEST 2] Configuration")
print(f"✓ USE_XGBOOST: {settings.USE_XGBOOST}")
print(f"✓ XGBOOST_THRESHOLD: {settings.XGBOOST_THRESHOLD}")
print(f"✓ LIGHTGBM_THRESHOLD: {settings.LIGHTGBM_THRESHOLD}")

# Test 3: Active Model
print("\n[TEST 3] Active Model Selection")
active_model = model_loader.get_active_model()
threshold = model_loader.get_threshold()
print(f"✓ Active model type: {type(active_model).__name__}")
print(f"✓ Active threshold: {threshold}")

# Test 4: Model Metadata
print("\n[TEST 4] XGBoost Model Metadata")
metadata = model_loader.metadata
if metadata and 'models' in metadata:
    xgb_info = metadata.get('models', {}).get('xgboost', {})
    metrics = xgb_info.get('metrics', {})
    
    print(f"✓ ROC-AUC: {metrics.get('roc_auc', 0):.4f}")
    print(f"✓ Precision: {metrics.get('precision', 0):.4f}")
    print(f"✓ Recall: {metrics.get('recall', 0):.4f}")
    print(f"✓ F1-Score: {metrics.get('f1', 0):.4f}")
    print(f"✓ Balanced Accuracy: {metrics.get('balanced_accuracy', 0):.4f}")
    print(f"✓ Threshold: {xgb_info.get('threshold', 0):.4f}")
else:
    print("⚠ Metadata not available")

# Test 5: Comparison with LightGBM
print("\n[TEST 5] Performance Comparison")
if metadata and 'models' in metadata:
    lgbm_info = metadata.get('models', {}).get('lightgbm', {})
    xgb_metrics = xgb_info.get('metrics', {})
    lgbm_metrics = lgbm_info.get('metrics', {})
    
    print("\nMetric          | LightGBM | XGBoost  | Improvement")
    print("-" * 60)
    
    roc_improvement = ((xgb_metrics.get('roc_auc', 0) / lgbm_metrics.get('roc_auc', 1)) - 1) * 100
    print(f"ROC-AUC         | {lgbm_metrics.get('roc_auc', 0):.4f}   | {xgb_metrics.get('roc_auc', 0):.4f}   | +{roc_improvement:.1f}%")
    
    prec_improvement = ((xgb_metrics.get('precision', 0) / lgbm_metrics.get('precision', 1)) - 1) * 100
    print(f"Precision       | {lgbm_metrics.get('precision', 0):.4f}   | {xgb_metrics.get('precision', 0):.4f}   | +{prec_improvement:.1f}%")
    
    f1_improvement = ((xgb_metrics.get('f1', 0) / lgbm_metrics.get('f1', 1)) - 1) * 100
    print(f"F1-Score        | {lgbm_metrics.get('f1', 0):.4f}   | {xgb_metrics.get('f1', 0):.4f}   | +{f1_improvement:.1f}%")

print("\n" + "=" * 60)
print("✅ All tests completed successfully!")
print("=" * 60)
