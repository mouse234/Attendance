# 📊 Smart Attendance Processor

This is a Flask-based web application designed to process attendance logs from `.dat` or `.xlsx` files and generate insightful reports. The app can convert raw log data into structured Excel sheets showing daily attendance and monthly summaries.

---

## ✨ Features

- 🔄 **DAT to Excel Conversion**  
  Automatically parses `.dat` files with tab-separated values and converts them into structured Excel format.

- 📅 **Previous Month Filtering**  
  Only processes entries from the previous calendar month for clean, timely reporting.

- ⏱ **Working Hours & Attendance Status**  
  Calculates in-time, out-time, working hours, and marks status as Full Day, Half Day, or Leave.

- 🕵️ **Short Leave Detection**  
  Smart detection of short leaves based on custom time rules.

- 📈 **Summary Sheet**  
  Generates a monthly summary including Full Days, Half Days, Short Leaves, and final calculated working days.

- 🔒 **Built-in User Database**  
  No need for a second upload. The app fetches user names from an internal database (`user_database.csv`).

---

## 🗂 File Structure

```bash
📁 your-project/
├── app.py                 # Flask app
├── user_database.csv      # Internal user ID to Name mapping
└── requirements.txt       # Python dependencies
