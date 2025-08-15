import os
import sys
import datetime
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from collections import Counter
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import smtplib
from io import BytesIO
import time
import re


# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MUST.settings')  # Replace with your project name
import django
django.setup()

from django.conf import settings

# Email configuration - modify these with your actual email
RECIPIENT_EMAIL = 'stephenondeyo0@gmail.com'  # Replace with your email
EMAIL_FROM = settings.EMAIL_HOST_USER
EMAIL_PASSWORD = settings.EMAIL_HOST_PASSWORD

def parse_log_entry(line):
    """Parse a log entry to extract important information."""
    if 'Request:' not in line:
        return None  # Skip non-request log entries
    
    timestamp_match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
    timestamp = timestamp_match.group(1) if timestamp_match else None
    
    request_match = re.search(r'Request: ([A-Z]+) (\/[^\s|]*)', line)
    method = request_match.group(1) if request_match else None
    endpoint = request_match.group(2) if request_match else None
    
    status_match = re.search(r'Status: (\d+)', line)
    status = int(status_match.group(1)) if status_match else None
    
    duration_match = re.search(r'Duration: ([\d.]+)s', line)
    duration = float(duration_match.group(1)) if duration_match else None
    
    ip_match = re.search(r'IP: ([^\s|]+)', line)
    ip = ip_match.group(1) if ip_match else None
    
    ua_match = re.search(r'User-Agent: ([^\s|]+)', line)
    user_agent = ua_match.group(1) if ua_match else None
    
    return {
        'timestamp': timestamp,
        'method': method,
        'endpoint': endpoint,
        'status': status,
        'duration': duration,
        'ip': ip,
        'user_agent': user_agent
    }
def generate_api_report():
    """Generate and send an API usage report for the last hour."""
    now = datetime.datetime.now()
    hour_ago = now - datetime.timedelta(hours=1)
    
    time_period = f"{hour_ago.strftime('%Y-%m-%d %H:%M')} to {now.strftime('%Y-%m-%d %H:%M')}"
    print(f"Generating report for: {time_period}")
    
    log_file = 'api_requests.log'
    if not os.path.exists(log_file):
        print(f'Warning: Log file {log_file} not found')
        return
    
    hour_ago_str = hour_ago.strftime('%Y-%m-%d %H')
    now_str = now.strftime('%Y-%m-%d %H')
    
    logs_data = []
    with open(log_file, 'r') as f:
        for line in f:
            if hour_ago_str in line or now_str in line:
                entry_data = parse_log_entry(line)
                if entry_data is None:  # Skip non-request entries
                    continue
                if entry_data['timestamp']:
                    entry_time = datetime.datetime.strptime(entry_data['timestamp'], '%Y-%m-%d %H:%M:%S')
                    if hour_ago <= entry_time <= now:
                        if entry_data['duration'] is None:
                            print(f"Missing duration in request log entry: {line.strip()}")
                        logs_data.append(entry_data)
    
    print(f"Found {len(logs_data)} log entries in the last hour")
    
    charts = generate_charts(logs_data)
    send_email_report(logs_data, charts, time_period)
def generate_charts(logs_data):
    """Generate charts for the API usage report."""
    df = pd.DataFrame(logs_data)
    if df.empty:
        return []
    
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp')
    
    charts = []
    
    # 1. Requests over time
    plt.figure(figsize=(10, 6))
    df['timestamp'].value_counts(sort=False).sort_index().plot(kind='line')
    plt.title('API Requests Over Time')
    plt.xlabel('Time')
    plt.ylabel('Number of Requests')
    plt.tight_layout()
    
    img_data = BytesIO()
    plt.savefig(img_data, format='png')
    img_data.seek(0)
    charts.append(('requests_over_time.png', img_data.getvalue()))
    plt.close()
    
    # 2. Status code distribution
    plt.figure(figsize=(8, 6))
    df['status'].value_counts().plot(kind='pie', autopct='%1.1f%%')
    plt.title('Response Status Codes')
    plt.ylabel('')
    plt.tight_layout()
    
    img_data = BytesIO()
    plt.savefig(img_data, format='png')
    img_data.seek(0)
    charts.append(('status_codes.png', img_data.getvalue()))
    plt.close()
    
    # 3. Top 5 endpoints
    plt.figure(figsize=(10, 6))
    df['endpoint'].value_counts().head(5).plot(kind='barh')
    plt.title('Top 5 Requested Endpoints')
    plt.xlabel('Number of Requests')
    plt.tight_layout()
    
    img_data = BytesIO()
    plt.savefig(img_data, format='png')
    img_data.seek(0)
    charts.append(('top_endpoints.png', img_data.getvalue()))
    plt.close()
    
    # 4. Response time distribution
    plt.figure(figsize=(10, 6))
    # Filter out None values for duration
    df_duration = df['duration'].dropna()
    if not df_duration.empty:
        df_duration.plot(kind='hist', bins=20)
        plt.title('Response Time Distribution')
        plt.xlabel('Response Time (seconds)')
        plt.ylabel('Frequency')
    else:
        plt.text(0.5, 0.5, 'No duration data available', 
                 horizontalalignment='center', verticalalignment='center')
        plt.title('Response Time Distribution')
    plt.tight_layout()
    
    img_data = BytesIO()
    plt.savefig(img_data, format='png')
    img_data.seek(0)
    charts.append(('response_times.png', img_data.getvalue()))
    plt.close()
    
    # 5. HTTP Methods distribution
    plt.figure(figsize=(8, 6))
    df['method'].value_counts().plot(kind='pie', autopct='%1.1f%%')
    plt.title('HTTP Methods')
    plt.ylabel('')
    plt.tight_layout()
    
    img_data = BytesIO()
    plt.savefig(img_data, format='png')
    img_data.seek(0)
    charts.append(('http_methods.png', img_data.getvalue()))
    plt.close()
    
    return charts

def send_email_report(logs_data, charts, time_period):
    """Send an email with the API usage report including charts."""
    msg = MIMEMultipart('related')
    msg['Subject'] = f'API Usage Report - {time_period}'
    msg['From'] = EMAIL_FROM
    msg['To'] = RECIPIENT_EMAIL
    
    # Create HTML content
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            tr:nth-child(even) {{ background-color: #f9f9f9; }}
            .chart {{ margin: 20px 0; text-align: center; }}
            .stats {{ margin: 20px 0; }}
        </style>
    </head>
    <body>
        <h1>API Usage Report for {time_period}</h1>
        
        <div class="stats">
            <h2>Summary Statistics</h2>
            <p><strong>Total Requests:</strong> {len(logs_data)}</p>
    """
    
    # Add more statistics if we have data
    if logs_data:
        df = pd.DataFrame(logs_data)
        
        # Status code counts
        status_counts = df['status'].value_counts()
        html += "<p><strong>Status Code Distribution:</strong></p>"
        html += "<ul>"
        for status, count in status_counts.items():
            html += f"<li>Status {status}: {count} requests ({count/len(df)*100:.1f}%)</li>"
        html += "</ul>"
        
        # Average response time (only if duration is not None)
        if 'duration' in df and df['duration'].notna().any():
            avg_time = df['duration'].mean()
            html += f"<p><strong>Average Response Time:</strong> {avg_time:.3f} seconds</p>"
        else:
            html += "<p><strong>Average Response Time:</strong> N/A</p>"
        
        # Top endpoints
        top_endpoints = df['endpoint'].value_counts().head(5)
        html += "<p><strong>Top 5 Endpoints:</strong></p>"
        html += "<ul>"
        for endpoint, count in top_endpoints.items():
            html += f"<li>{endpoint}: {count} requests</li>"
        html += "</ul>"
        
        # Unique IPs and user agents
        unique_ips = df['ip'].nunique()
        unique_agents = df['user_agent'].nunique()
        html += f"<p><strong>Unique Client IPs:</strong> {unique_ips}</p>"
        html += f"<p><strong>Unique User Agents:</strong> {unique_agents}</p>"
    
    # Add charts to the HTML
    for i, (chart_name, _) in enumerate(charts):
        html += f"""
        <div class="chart">
            <h2>{chart_name.split('.')[0].replace('_', ' ').title()}</h2>
            <img src="cid:chart{i}" alt="{chart_name}" width="700">
        </div>
        """
    
    # Add recent requests table if we have data
    if logs_data:
        # Only show the most recent 10 requests
        recent_logs = logs_data[-10:] if len(logs_data) > 10 else logs_data
        
        html += """
        <h2>Recent Requests</h2>
        <table>
            <tr>
                <th>Time</th>
                <th>Method</th>
                <th>Endpoint</th>
                <th>Status</th>
                <th>Duration (s)</th>
                <th>Client IP</th>
                <th>User Agent</th>
            </tr>
        """
        
        for log in reversed(recent_logs):  # Show most recent first
            # Handle None values for duration
            duration_display = f"{log['duration']:.3f}" if log['duration'] is not None else "N/A"
            html += f"""
            <tr>
                <td>{log['timestamp'] or 'N/A'}</td>
                <td>{log['method'] or 'N/A'}</td>
                <td>{log['endpoint'] or 'N/A'}</td>
                <td>{log['status'] or 'N/A'}</td>
                <td>{duration_display}</td>
                <td>{log['ip'] or 'N/A'}</td>
                <td>{log['user_agent'] or 'N/A'}</td>
            </tr>
            """
        
        html += "</table>"
    
    html += """
        <p>This report is generated automatically every hour.</p>
    </body>
    </html>
    """
    
    # Attach HTML content
    msg_alternative = MIMEMultipart('alternative')
    msg_alternative.attach(MIMEText(html, 'html'))
    msg.attach(msg_alternative)
    
    # Attach charts
    for i, (chart_name, chart_data) in enumerate(charts):
        img = MIMEImage(chart_data)
        img.add_header('Content-ID', f'<chart{i}>')
        img.add_header('Content-Disposition', 'inline', filename=chart_name)
        msg.attach(img)
    
    # Send the email
    try:
        server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_FROM, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"Email report sent successfully to {RECIPIENT_EMAIL}")
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        import traceback
        traceback.print_exc()
        return False
def run_hourly():
    """Run the report generation every hour."""
    while True:
        try:
            generate_api_report()
        except Exception as e:
            print(f"Error generating report: {e}")
            import traceback
            traceback.print_exc()
        
        # Sleep until the next hour
        now = datetime.datetime.now()
        next_hour = (now + datetime.timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
        sleep_seconds = (next_hour - now).total_seconds()
        
        print(f"Next report will be generated in {sleep_seconds:.0f} seconds (at {next_hour})")
        time.sleep(sleep_seconds)

if __name__ == "__main__":
    # For testing, run once immediately
    generate_api_report()
    
    # Then start the hourly schedule
    run_hourly()