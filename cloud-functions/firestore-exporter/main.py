"""
Firestore to GCS Exporter
Exports loan_applications and student_applications collections to GCS for model retraining
"""

from google.cloud import firestore, storage
import pandas as pd
from datetime import datetime
import json
import os
import functions_framework
from typing import Any, Dict, cast


def _save_parquet_and_metadata(
    bucket,
    records,
    dataset_name: str,
    timestamp: str,
    label_column: str,
    source_collection: str,
):
    """Persist dataset records and metadata to GCS and return file info."""
    if not records:
        return None

    df = pd.DataFrame(records)
    output_path = f'/tmp/{dataset_name}_{timestamp}.parquet'
    df.to_parquet(output_path, index=False)

    parquet_blob_path = f'data/exports/{dataset_name}_{timestamp}.parquet'
    blob = bucket.blob(parquet_blob_path)
    blob.upload_from_filename(output_path)

    metadata = {
        'export_timestamp': timestamp,
        'dataset_name': dataset_name,
        'source_collection': source_collection,
        'total_records': len(records),
        'labeled_records': df[label_column].notna().sum() if label_column in df.columns else 0,
        'date_range': {
            'earliest': df['timestamp'].min().isoformat() if 'timestamp' in df.columns else None,
            'latest': df['timestamp'].max().isoformat() if 'timestamp' in df.columns else None,
        },
        'gcs_path': f'gs://{bucket.name}/{parquet_blob_path}',
    }

    metadata_blob_path = f'data/exports/metadata_{dataset_name}_{timestamp}.json'
    metadata_blob = bucket.blob(metadata_blob_path)
    metadata_blob.upload_from_string(json.dumps(metadata, indent=2, default=str))

    return {
        'records_exported': len(records),
        'labeled_records': metadata['labeled_records'],
        'gcs_path': metadata['gcs_path'],
        'metadata_path': f'gs://{bucket.name}/{metadata_blob_path}',
    }


@functions_framework.http
def export_firestore_to_gcs(request):
    """
    Export loan_applications and student_applications from Firestore to GCS
    Triggered: Scheduled (weekly) or manual HTTP call
    
    Returns:
        dict: Export status and record count
    """
    try:
        db = firestore.Client()
        storage_client = storage.Client()
        # Allow bucket override per environment to support different projects.
        export_bucket = os.getenv('GCS_EXPORT_BUCKET', 'credit-scoring-retrain-513943636250')
        bucket = storage_client.bucket(export_bucket)
        
        # Query all scored standard applications
        applications_ref = db.collection('loan_applications')
        query = applications_ref.where('status', '==', 'scored')
        
        docs = query.stream()
        loan_records = []
        
        for doc in docs:
            doc_data = doc.to_dict()
            if not doc_data:
                continue
            
            # Cast to ensure type checker knows this is a dict
            data = cast(Dict[str, Any], doc_data)
            
            loan_records.append({
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

        # Query student applications
        student_ref = db.collection('student_applications')
        student_query = student_ref.where('status', 'in', ['scored', 'rejected'])
        student_docs = student_query.stream()
        student_records = []

        for doc in student_docs:
            doc_data = doc.to_dict()
            if not doc_data:
                continue

            data = cast(Dict[str, Any], doc_data)

            student_records.append({
                'application_id': doc.id,
                'user_id': data.get('userId'),
                'timestamp': data.get('createdAt'),
                'status': data.get('status'),
                'reason': data.get('reason'),
                'manual_review': data.get('manual_review', False),
                'gpa_latest': data.get('gpa_latest'),
                'academic_year': data.get('academic_year'),
                'major': data.get('major'),
                'program_level': data.get('program_level'),
                'living_status': data.get('living_status'),
                'loan_amount': data.get('loan_amount'),
                'has_buffer': data.get('has_buffer'),
                'support_sources': data.get('support_sources', []),
                'monthly_income': data.get('monthly_income'),
                'monthly_expenses': data.get('monthly_expenses'),
                'model_score': data.get('model_score'),
                'credit_score': data.get('credit_score'),
                'loan_limit_vnd': data.get('loan_limit_vnd'),
                'risk_level': data.get('risk_level'),
                'approved': data.get('approved'),
                'label': data.get('label', None),
                'repayment_status': data.get('repayment_status', None),
            })
        
        if not loan_records and not student_records:
            return {
                'status': 'success',
                'records_exported': 0,
                'message': 'No records found to export'
            }

        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')

        loan_export = _save_parquet_and_metadata(
            bucket=bucket,
            records=loan_records,
            dataset_name='loan_applications',
            timestamp=timestamp,
            label_column='actual_default',
            source_collection='loan_applications',
        )
        student_export = _save_parquet_and_metadata(
            bucket=bucket,
            records=student_records,
            dataset_name='student_applications',
            timestamp=timestamp,
            label_column='label',
            source_collection='student_applications',
        )

        total_records = len(loan_records) + len(student_records)
        total_labeled = 0
        if loan_export:
            total_labeled += loan_export['labeled_records']
        if student_export:
            total_labeled += student_export['labeled_records']
        
        return {
            'status': 'success',
            'records_exported': total_records,
            'labeled_records': total_labeled,
            'loan_applications': loan_export,
            'student_applications': student_export,
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }, 500
