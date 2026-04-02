"""
Email notification service for model retraining pipeline
Uses Gmail SMTP
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, Optional


def send_email_notification(
    subject: str,
    metrics: Dict[str, Any],
    prod_metrics: Optional[Dict[str, Any]] = None,
    promoted: bool = False,
    timestamp: str = None
):
    """
    Send email notification with training results via Gmail SMTP
    
    Args:
        subject: Email subject
        metrics: New model metrics
        prod_metrics: Production model metrics (if exists)
        promoted: Whether model was promoted
        timestamp: Training timestamp
    """
    recipient = os.getenv('NOTIFICATION_EMAIL', 'vanquoc11082004@gmail.com')
    
    if not recipient:
        print("No notification email configured. Skipping notification.")
        return
    
    html_body = generate_html_report(metrics, prod_metrics, promoted, timestamp)
    send_via_gmail(recipient, subject, html_body)


def generate_html_report(
    metrics: Dict[str, Any],
    prod_metrics: Optional[Dict[str, Any]],
    promoted: bool,
    timestamp: str
) -> str:
    """Generate HTML email report"""
    report_bucket = os.getenv('GCS_BUCKET', 'credit-scoring-retrain-513943636250')
    
    status_color = "#4CAF50" if promoted else "#FF9800"
    status_text = "✅ MODEL PROMOTED TO PRODUCTION" if promoted else "⚠️ MODEL SAVED TO STAGING (Not Promoted)"
    
    # Calculate improvements
    improvement_section = ""
    if prod_metrics:
        auc_diff = metrics['auc_roc'] - prod_metrics['auc_roc']
        precision_diff = metrics['precision'] - prod_metrics['precision']
        recall_diff = metrics['recall'] - prod_metrics['recall']
        
        improvement_section = f"""
        <h2>📊 Model Comparison</h2>
        <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
            <tr style="background-color: #f5f5f5;">
                <th style="padding: 12px; border: 1px solid #ddd; text-align: left;">Metric</th>
                <th style="padding: 12px; border: 1px solid #ddd; text-align: center;">Production</th>
                <th style="padding: 12px; border: 1px solid #ddd; text-align: center;">New Model</th>
                <th style="padding: 12px; border: 1px solid #ddd; text-align: center;">Change</th>
            </tr>
            <tr>
                <td style="padding: 12px; border: 1px solid #ddd;"><strong>AUC-ROC</strong></td>
                <td style="padding: 12px; border: 1px solid #ddd; text-align: center;">{prod_metrics['auc_roc']:.4f}</td>
                <td style="padding: 12px; border: 1px solid #ddd; text-align: center;">{metrics['auc_roc']:.4f}</td>
                <td style="padding: 12px; border: 1px solid #ddd; text-align: center; color: {'green' if auc_diff > 0 else 'red'};">
                    {auc_diff:+.4f} ({(auc_diff/prod_metrics['auc_roc']*100):+.2f}%)
                </td>
            </tr>
            <tr style="background-color: #f9f9f9;">
                <td style="padding: 12px; border: 1px solid #ddd;"><strong>Precision</strong></td>
                <td style="padding: 12px; border: 1px solid #ddd; text-align: center;">{prod_metrics['precision']:.4f}</td>
                <td style="padding: 12px; border: 1px solid #ddd; text-align: center;">{metrics['precision']:.4f}</td>
                <td style="padding: 12px; border: 1px solid #ddd; text-align: center; color: {'green' if precision_diff > 0 else 'red'};">
                    {precision_diff:+.4f}
                </td>
            </tr>
            <tr>
                <td style="padding: 12px; border: 1px solid #ddd;"><strong>Recall</strong></td>
                <td style="padding: 12px; border: 1px solid #ddd; text-align: center;">{prod_metrics['recall']:.4f}</td>
                <td style="padding: 12px; border: 1px solid #ddd; text-align: center;">{metrics['recall']:.4f}</td>
                <td style="padding: 12px; border: 1px solid #ddd; text-align: center; color: {'green' if recall_diff > 0 else 'red'};">
                    {recall_diff:+.4f}
                </td>
            </tr>
        </table>
        """
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: {status_color}; color: white; padding: 20px; border-radius: 5px; }}
            .metrics {{ margin: 20px 0; }}
            .metric-row {{ padding: 10px; border-bottom: 1px solid #eee; }}
            .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1 style="margin: 0;">🤖 Credit Scoring Model Retraining Report</h1>
                <p style="margin: 10px 0 0 0;">{status_text}</p>
            </div>
            
            <div class="metrics">
                <h2>📈 New Model Performance</h2>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr style="background-color: #f5f5f5;">
                        <td style="padding: 12px; border: 1px solid #ddd;"><strong>AUC-ROC</strong></td>
                        <td style="padding: 12px; border: 1px solid #ddd;">{metrics['auc_roc']:.4f}</td>
                    </tr>
                    <tr>
                        <td style="padding: 12px; border: 1px solid #ddd;"><strong>Precision</strong></td>
                        <td style="padding: 12px; border: 1px solid #ddd;">{metrics['precision']:.4f}</td>
                    </tr>
                    <tr style="background-color: #f5f5f5;">
                        <td style="padding: 12px; border: 1px solid #ddd;"><strong>Recall</strong></td>
                        <td style="padding: 12px; border: 1px solid #ddd;">{metrics['recall']:.4f}</td>
                    </tr>
                    <tr>
                        <td style="padding: 12px; border: 1px solid #ddd;"><strong>F1-Score</strong></td>
                        <td style="padding: 12px; border: 1px solid #ddd;">{metrics['f1_score']:.4f}</td>
                    </tr>
                    <tr style="background-color: #f5f5f5;">
                        <td style="padding: 12px; border: 1px solid #ddd;"><strong>Test Samples</strong></td>
                        <td style="padding: 12px; border: 1px solid #ddd;">{metrics['n_samples']}</td>
                    </tr>
                    <tr>
                        <td style="padding: 12px; border: 1px solid #ddd;"><strong>Positive Rate</strong></td>
                        <td style="padding: 12px; border: 1px solid #ddd;">{metrics['positive_rate']:.2%}</td>
                    </tr>
                    <tr style="background-color: #f5f5f5;">
                        <td style="padding: 12px; border: 1px solid #ddd;"><strong>Decision Threshold</strong></td>
                        <td style="padding: 12px; border: 1px solid #ddd;">{metrics['threshold']:.2f}</td>
                    </tr>
                </table>
                
                {improvement_section}
                
                <h2>ℹ️ Training Information</h2>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 12px; border: 1px solid #ddd;"><strong>Timestamp</strong></td>
                        <td style="padding: 12px; border: 1px solid #ddd;">{timestamp or 'N/A'}</td>
                    </tr>
                    <tr style="background-color: #f5f5f5;">
                        <td style="padding: 12px; border: 1px solid #ddd;"><strong>GCS Bucket</strong></td>
                        <td style="padding: 12px; border: 1px solid #ddd;">{report_bucket}</td>
                    </tr>
                    <tr>
                        <td style="padding: 12px; border: 1px solid #ddd;"><strong>Model Location</strong></td>
                        <td style="padding: 12px; border: 1px solid #ddd;">
                            {"models/production/" if promoted else "models/staging/"}
                        </td>
                    </tr>
                </table>
                
                <p style="margin-top: 20px;">
                    <a href="https://console.cloud.google.com/storage/browser/{report_bucket}/models" 
                       style="background-color: #2196F3; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">
                        📁 View Models in GCS
                    </a>
                </p>
            </div>
            
            <div class="footer">
                <p>This is an automated notification from Credit Scoring Model Retraining Pipeline.</p>
                <p>Execution Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html


def send_via_gmail(recipient: str, subject: str, html_body: str):
    """Send email via Gmail SMTP"""
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        sender_email = os.getenv('GMAIL_USER')
        sender_password = os.getenv('GMAIL_APP_PASSWORD')  # Use App Password, not regular password
        
        if not sender_email or not sender_password:
            print("ERROR: GMAIL_USER and GMAIL_APP_PASSWORD not configured")
            return
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = recipient
        
        html_part = MIMEText(html_body, 'html')
        msg.attach(html_part)
        
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient, msg.as_string())
        
        print(f"✓ Email sent via Gmail to {recipient}")
        
    except Exception as e:
        print(f"ERROR sending email via Gmail: {e}")
