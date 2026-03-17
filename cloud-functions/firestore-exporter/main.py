"""
Firestore to GCS Exporter
Exports loan_applications collection to GCS for model retraining
"""

from google.cloud import firestore, storage
import pandas as pd
from datetime import datetime
import json
import os
import functions_framework
from typing import Any, Dict, cast


@functions_framework.http
def export_firestore_to_gcs(request):
    """
    Export loan_applications from Firestore to GCS
    Triggered: Scheduled (weekly) or manual HTTP call
    
    Returns:
        dict: Export status and record count
    """
    try:
        db = firestore.Client()
        storage_client = storage.Client()
        # Allow bucket override per environment to support different projects.
        export_bucket = os.getenv('GCS_EXPORT_BUCKET', 'mlretrain')
        bucket = storage_client.bucket(export_bucket)
        
        # Query all scored applications
        applications_ref = db.collection('loan_applications')
        query = applications_ref.where('status', '==', 'scored')
        
        docs = query.stream()
        records = []
        
        for doc in docs:
            doc_data = doc.to_dict()
            if not doc_data:
                continue
            
            # Cast to ensure type checker knows this is a dict
            data = cast(Dict[str, Any], doc_data)
            
            records.append({
                'application_id': doc.id,
                'user_id': data.get('userId'),
                'timestamp': data.get('createdAt'),
                
                # Input features (for retraining)
                'age': data.get('age'),
                'monthly_income': data.get('monthlyIncome'),
                'employment_status': data.get('employmentStatus'),
                'years_employed': data.get('yearsEmployed'),
                'home_ownership': data.get('homeOwnership'),
                'loan_purpose': data.get('loanPurpose'),
                'years_credit_history': data.get('yearsCreditHistory'),
                'has_previous_defaults': data.get('hasPreviousDefaults'),
                'currently_defaulting': data.get('currentlyDefaulting'),
                
                # Model outputs (for monitoring)
                'credit_score': data.get('creditScore'),
                'approved_limit': data.get('approvedLimit'),
                'risk_level': data.get('riskLevel'),
                'approved': data.get('approved'),
                'interest_rate': data.get('interestRate'),
                'loan_term_months': data.get('loanTermMonths'),
                
                # Label (will be null initially)
                'actual_default': data.get('actualDefault', None),
                'loan_outcome_date': data.get('loanOutcomeDate', None),
            })
        
        if not records:
            return {
                'status': 'success',
                'records_exported': 0,
                'message': 'No records found to export'
            }
        
        # Convert to DataFrame and save as parquet
        df = pd.DataFrame(records)
        
        # Save to GCS
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        output_path = f'/tmp/loan_applications_{timestamp}.parquet'
        df.to_parquet(output_path, index=False)
        
        blob = bucket.blob(f'data/exports/loan_applications_{timestamp}.parquet')
        blob.upload_from_filename(output_path)
        
        # Also save metadata
        metadata = {
            'export_timestamp': timestamp,
            'total_records': len(records),
            'labeled_records': df['actual_default'].notna().sum(),
            'date_range': {
                'earliest': df['timestamp'].min().isoformat() if 'timestamp' in df.columns else None,
                'latest': df['timestamp'].max().isoformat() if 'timestamp' in df.columns else None,
            },
            'gcs_path': f'gs://{export_bucket}/data/exports/loan_applications_{timestamp}.parquet'
        }
        
        metadata_blob = bucket.blob(f'data/exports/metadata_{timestamp}.json')
        metadata_blob.upload_from_string(json.dumps(metadata, indent=2, default=str))
        
        return {
            'status': 'success',
            'records_exported': len(records),
            'labeled_records': metadata['labeled_records'],
            'gcs_path': metadata['gcs_path'],
            'metadata_path': f'gs://{export_bucket}/data/exports/metadata_{timestamp}.json'
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }, 500
