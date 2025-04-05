import pandas as pd
from datetime import datetime, timedelta

def process_attendance_data(file_path):
    # Read the Excel file
    df = pd.read_excel("/content/attendance_log.xlsx")

    # Convert Timestamp column to datetime
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])

    # Get current date and calculate previous month
    current_date = datetime.now()
    previous_month = current_date.month - 1 if current_date.month > 1 else 12
    previous_year = current_date.year if current_date.month > 1 else current_date.year - 1

    # Filter data for previous month only
    df = df[(df['Timestamp'].dt.month == previous_month) &
            (df['Timestamp'].dt.year == previous_year)]

    # If no data found for previous month
    if df.empty:
        print(f"No data found for {current_date.strftime('%B %Y')}")
        return pd.DataFrame(), pd.DataFrame()

    # Extract date and time components
    df['Date'] = df['Timestamp'].dt.date
    df['Time'] = df['Timestamp'].dt.time
    df['Day'] = df['Timestamp'].dt.day_name()

    # Sort by User ID and Timestamp
    df = df.sort_values(['User ID', 'Timestamp'])

    # Group by User ID and Date
    grouped = df.groupby(['User ID', 'Date'])

    # Initialize result dataframe
    result = pd.DataFrame(columns=[
        'Serial No',
        'User ID',
        'Name',
        'Date',
        'Day',
        'In Time',
        'Out Time',
        'Working Hours',
        'Attendance Status',
        'Short Leave',
        'Remarks'
    ])

    # Initialize summary dataframe
    summary = pd.DataFrame(columns=[
        'Serial No',
        'User ID',
        'Name',
        'Full Days',
        'Half Days',
        'Short Leaves',
        'Total Working Days',
        'Remarks'
    ])

    serial_no = 1
    user_summaries = {}

    for (user_id, date), group in grouped:
        # Get all timestamps for this user on this date
        timestamps = group['Timestamp'].tolist()

        # Initialize remarks
        remarks = ""

        # Check for single entry (only in or out time)
        if len(timestamps) == 1:
            remarks = "Supervision Required - Single Entry"

        # Process in time (first timestamp)
        in_time = timestamps[0]

        # Process out time (last timestamp)
        out_time = timestamps[-1] if len(timestamps) > 1 else in_time  # Use same time if only one entry

        # Calculate working hours
        working_hours = (out_time - in_time).total_seconds() / 3600 if len(timestamps) > 1 else 0

        # Determine attendance status
        if working_hours < 4:
            status = 'Leave'
        elif 4 <= working_hours < 7:
            status = 'Half Day'
        else:
            status = 'Full Day'

        # Check for short leave conditions
        short_leave = 'No'
        in_time_obj = in_time.time()
        out_time_obj = out_time.time()

        # Condition 1: In time between 10:46-11:40 AND out time after 19:00
        condition1 = (datetime.strptime('10:46', '%H:%M').time() <= in_time_obj <= datetime.strptime('11:40', '%H:%M').time() and
                     out_time_obj >= datetime.strptime('19:00', '%H:%M').time())

        # Condition 2: In time between 10:20-10:46 AND out time between 18:00-18:30
        condition2 = (datetime.strptime('10:20', '%H:%M').time() <= in_time_obj <= datetime.strptime('10:46', '%H:%M').time() and
                     datetime.strptime('18:00', '%H:%M').time() <= out_time_obj <= datetime.strptime('18:30', '%H:%M').time())

        if condition1 or condition2:
            short_leave = 'Yes'

        # Get day name
        day_name = in_time.strftime('%A')

        # Add to result dataframe
        result.loc[len(result)] = [
            serial_no,
            user_id,
            '',  # Empty name column
            date,
            day_name,
            in_time.time(),
            out_time.time(),
            round(working_hours, 2),
            status,
            short_leave,
            remarks
        ]

    # Process summary data after all records are processed
    unique_users = result['User ID'].unique()
    summary_serial_no = 1

    for user_id in unique_users:
        user_data = result[result['User ID'] == user_id]

        # Calculate metrics
        full_days = len(user_data[user_data['Attendance Status'] == 'Full Day'])
        half_days = len(user_data[user_data['Attendance Status'] == 'Half Day'])
        short_leaves = len(user_data[user_data['Short Leave'] == 'Yes'])

        # Calculate total working days with new formula
        total_working_days = round(full_days + (half_days / 2) - ((short_leaves-2) / 4), 2)

        # Check if user has any single entry remarks
        user_remarks = user_data['Remarks'].unique()
        summary_remark = ""
        if "Supervision Required - Single Entry" in user_remarks:
            summary_remark = "Has incomplete attendance records (single entries)"

        # Add to summary dataframe with float types
        summary.loc[len(summary)] = [
            summary_serial_no,
            user_id,
            '',  # Empty name column
            float(full_days),
            float(half_days),
            float(short_leaves),
            float(total_working_days),
            summary_remark
        ]

        summary_serial_no += 1

    # Identify public holidays (days that aren't Sunday with no attendance records)
    all_dates_in_month = pd.date_range(
        start=f"{previous_year}-{previous_month}-01",
        end=f"{previous_year}-{previous_month}-{pd.Timestamp(previous_year, previous_month, 1).days_in_month}",
        freq='D'
    )

    # Filter out Sundays
    working_days = [d for d in all_dates_in_month if d.day_name() != 'Sunday']

    # Find dates with no attendance records
    dates_with_data = pd.to_datetime(result['Date']).unique()
    public_holidays = [d for d in working_days if d not in dates_with_data]

    # Add public holidays to summary
    if public_holidays:
        summary['Public Holidays'] = ', '.join([d.strftime('%Y-%m-%d') for d in public_holidays])

    return result, summary

# Example usage
if __name__ == "__main__":
    input_file = "attendance_log.xlsx"
    output_file = "processed_attendance.xlsx"
    summary_file = "attendance_summary.xlsx"

    processed_data, summary_data = process_attendance_data(input_file)

    if not processed_data.empty:
        # Format all float columns to 2 decimal places in summary
        float_cols = ['Full Days', 'Half Days', 'Short Leaves', 'Total Working Days']
        summary_data[float_cols] = summary_data[float_cols].applymap(lambda x: f"{float(x):.2f}")

        processed_data.to_excel(output_file, index=False)
        summary_data.to_excel(summary_file, index=False)
        print(f"Processed data for previous month saved to {output_file}")
        print(f"Summary data saved to {summary_file}")
    else:
        print("No data to process for previous month.")
