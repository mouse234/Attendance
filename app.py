from flask import Flask, request, send_file
import pandas as pd
from io import BytesIO
from datetime import datetime

app = Flask(__name__)


def process_attendance_data(excel_file):
    df = pd.read_excel(excel_file)

    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    current_date = datetime.now()
    previous_month = current_date.month - 1 if current_date.month > 1 else 12
    previous_year = current_date.year if current_date.month > 1 else current_date.year - 1

    df = df[(df['Timestamp'].dt.month == previous_month) &
            (df['Timestamp'].dt.year == previous_year)]

    if df.empty:
        return None, None

    df['Date'] = df['Timestamp'].dt.date
    df['Time'] = df['Timestamp'].dt.time
    df['Day'] = df['Timestamp'].dt.day_name()
    df = df.sort_values(['User ID', 'Timestamp'])
    grouped = df.groupby(['User ID', 'Date'])

    result = pd.DataFrame(columns=[
        'Serial No', 'User ID', 'Name', 'Date', 'Day', 'In Time', 'Out Time',
        'Working Hours', 'Attendance Status', 'Short Leave', 'Remarks'])

    summary = pd.DataFrame(columns=[
        'Serial No', 'User ID', 'Name', 'Full Days', 'Half Days',
        'Short Leaves', 'Total Working Days', 'Remarks'])

    serial_no = 1
    for (user_id, date), group in grouped:
        timestamps = group['Timestamp'].tolist()
        remarks = ""
        if len(timestamps) == 1:
            remarks = "Supervision Required - Single Entry"

        in_time = timestamps[0]
        out_time = timestamps[-1] if len(timestamps) > 1 else in_time
        working_hours = (out_time - in_time).total_seconds() / 3600 if len(timestamps) > 1 else 0

        if working_hours < 4:
            status = 'Leave'
        elif 4 <= working_hours < 7:
            status = 'Half Day'
        else:
            status = 'Full Day'

        short_leave = 'No'
        in_time_obj = in_time.time()
        out_time_obj = out_time.time()

        condition1 = (datetime.strptime('10:46', '%H:%M').time() <= in_time_obj <= datetime.strptime('11:40', '%H:%M').time() and
                      out_time_obj >= datetime.strptime('19:00', '%H:%M').time())
        condition2 = (datetime.strptime('10:20', '%H:%M').time() <= in_time_obj <= datetime.strptime('10:46', '%H:%M').time() and
                      datetime.strptime('18:00', '%H:%M').time() <= out_time_obj <= datetime.strptime('18:30', '%H:%M').time())

        if condition1 or condition2:
            short_leave = 'Yes'

        day_name = in_time.strftime('%A')

        result.loc[len(result)] = [
            serial_no, user_id, '', date, day_name,
            in_time.time(), out_time.time(), round(working_hours, 2),
            status, short_leave, remarks
        ]

        serial_no += 1

    unique_users = result['User ID'].unique()
    summary_serial_no = 1

    for user_id in unique_users:
        user_data = result[result['User ID'] == user_id]
        full_days = len(user_data[user_data['Attendance Status'] == 'Full Day'])
        half_days = len(user_data[user_data['Attendance Status'] == 'Half Day'])
        short_leaves = len(user_data[user_data['Short Leave'] == 'Yes'])
        total_working_days = round(full_days + (half_days / 2) - ((short_leaves-2) / 4), 2)
        user_remarks = user_data['Remarks'].unique()
        summary_remark = ""
        if "Supervision Required - Single Entry" in user_remarks:
            summary_remark = "Has incomplete attendance records (single entries)"

        summary.loc[len(summary)] = [
            summary_serial_no, user_id, '', float(full_days), float(half_days),
            float(short_leaves), float(total_working_days), summary_remark
        ]
        summary_serial_no += 1

    return result, summary


@app.route('/', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if not file.filename.endswith('.xlsx'):
            return 'Invalid file format. Please upload an .xlsx file.'

        processed_data, summary_data = process_attendance_data(file)
        if processed_data is None:
            return "No data found for previous month."

        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            processed_data.to_excel(writer, index=False, sheet_name='Processed Attendance')
            summary_data.to_excel(writer, index=False, sheet_name='Summary')

        output.seek(0)
        return send_file(output, as_attachment=True, download_name='attendance_report.xlsx')

    return '''
        <h1>Upload Attendance Excel File</h1>
        <form method="post" enctype="multipart/form-data">
            <input type="file" name="file" accept=".xlsx">
            <input type="submit">
        </form>
    '''


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
