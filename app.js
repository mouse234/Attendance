import express from 'express';
import fileUpload from 'express-fileupload';
import XLSX from 'xlsx';
import { parse } from 'csv-parse/sync';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const app = express();

app.use(express.static('public'));
app.use(fileUpload());
app.set('view engine', 'ejs');

// Convert templates to EJS
app.set('views', path.join(__dirname, 'views'));

function convertDatToExcel(datContent) {
    const records = parse(datContent, {
        delimiter: '\t',
        columns: ['User ID', 'Timestamp', 'Col3', 'Col4', 'Col5', 'Col6']
    });

    const worksheet = XLSX.utils.json_to_sheet(records);
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, 'Raw Attendance');
    
    return XLSX.write(workbook, { type: 'buffer', bookType: 'xlsx' });
}

function processAttendanceData(excelData, userNameMap) {
    const workbook = XLSX.read(excelData);
    const worksheet = workbook.Sheets[workbook.SheetNames[0]];
    const data = XLSX.utils.sheet_to_json(worksheet);

    const currentDate = new Date();
    const previousMonth = currentDate.getMonth() === 0 ? 11 : currentDate.getMonth() - 1;
    const previousYear = currentDate.getMonth() === 0 ? currentDate.getFullYear() - 1 : currentDate.getFullYear();

    const filteredData = data.filter(row => {
        const timestamp = new Date(row.Timestamp);
        return timestamp.getMonth() === previousMonth && timestamp.getFullYear() === previousYear;
    });

    if (filteredData.length === 0) {
        return [null, null, previousMonth + 1, previousYear];
    }

    // Process attendance similar to Python version
    const summary = processAttendanceSummary(filteredData, userNameMap);
    
    return [filteredData, summary, previousMonth + 1, previousYear];
}

function processAttendanceSummary(data, userNameMap) {
    // Group by user and date
    const groupedData = data.reduce((acc, row) => {
        const userId = row['User ID'];
        if (!acc[userId]) acc[userId] = { fullDays: 0, halfDays: 0, shortLeaves: 0 };
        
        // Calculate attendance metrics
        const timestamp = new Date(row.Timestamp);
        const hours = timestamp.getHours();
        
        if (hours >= 9) acc[userId].fullDays++;
        else if (hours >= 4) acc[userId].halfDays++;
        
        return acc;
    }, {});

    return Object.entries(groupedData).map(([userId, stats]) => ({
        'User ID': userId,
        'Name': userNameMap[userId] || '',
        'Full Days': stats.fullDays,
        'Half Days': stats.halfDays,
        'Short Leaves': stats.shortLeaves,
        'Total Working Days': stats.fullDays + (stats.halfDays / 2)
    }));
}

app.get('/', (req, res) => {
    res.render('index');
});

app.post('/process', async (req, res) => {
    try {
        if (!req.files || !req.files.file) {
            return res.status(400).json({ error: 'No file uploaded' });
        }

        const file = req.files.file;
        let fileBuffer;

        if (file.name.endsWith('.dat')) {
            fileBuffer = convertDatToExcel(file.data.toString());
        } else if (file.name.endsWith('.xlsx')) {
            fileBuffer = file.data;
        } else {
            return res.status(400).json({ error: 'Invalid file format' });
        }

        const userDb = parse(fs.readFileSync('user_database.csv'), {
            columns: true,
            skip_empty_lines: true
        });

        const userNameMap = userDb.reduce((acc, row) => {
            acc[row['User ID']] = row['Name'];
            return acc;
        }, {});

        const [processedData, summaryData, month, year] = processAttendanceData(fileBuffer, userNameMap);

        if (!processedData) {
            return res.status(404).json({ error: 'No data found for previous month' });
        }

        res.render('summary', {
            summary: summaryData,
            month,
            year
        });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

app.get('/salary-slip/:userId', (req, res) => {
    try {
        const userDb = parse(fs.readFileSync('user_database.csv'), {
            columns: true,
            skip_empty_lines: true
        });

        const user = userDb.find(row => row['User ID'] === req.params.userId);
        
        if (!user) {
            throw new Error('User not found');
        }

        res.render('salary_slip', {
            user_id: req.params.userId,
            name: user.Name
        });
    } catch (error) {
        res.status(500).send(`Error: ${error.message}`);
    }
});

const PORT = process.env.PORT || 10000;
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});