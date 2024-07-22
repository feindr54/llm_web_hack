const express = require('express');
const mysql = require('mysql2');
const bodyParser = require('body-parser');
const path = require('path');

const app = express();
const port = 3000;

// Middleware
app.use(bodyParser.json());
app.use(express.static(path.join(__dirname, 'public')));

// MySQL connection
const db = mysql.createConnection({
    host: 'localhost',
    user: 'root',
    password: process.env.SQL_PW,
    database: 'webappdb'
});

db.connect((err) => {
    if (err) {
        console.error('Database connection failed: ' + err.stack);
        return;
    }
    console.log('Connected to database.');
});

// Routes
app.post('/login', (req, res) => {
    const { username, password } = req.body;

    console.log(username)
    console.log(password)

    const query = "SELECT * FROM users WHERE user = '" + username + " ' AND password = '" + password + "';"

    console.log("query: " + query)
    db.query(query, [username, password], (err, results) => {
        if (err) {
            res.status(500).json({ success: false, message: 'Database query error' });
            return;
        }

        if (results.length > 0) {
            res.json({ success: true });
        } else {
            res.json({ success: false });
        }
    });
});

app.listen(port, () => {
    console.log(`Server is running on http://localhost:${port}`);
});
