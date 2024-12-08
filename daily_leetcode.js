const express = require('express');
const cors = require('cors');
const { LeetCode } = require('leetcode-query');

const app = express();

// Middleware to handle CORS and JSON requests
app.use(express.json());
app.use(
  cors({
    origin: '*', // Allow all origins
  })
);

// Function to fetch the daily LeetCode problem
async function main() {
    console.log('Fetching daily question');
    const lc = new LeetCode();
    let daily = '';
    try {
      // Fetch the daily problem
      daily = await lc.daily();
    } catch (e) {
    }
    return daily;
  }
  

// Cache the result of the daily problem (first fetch)
const _cache = main();

// Endpoint to get the daily problem
app.get('/', async (req, res) => {
  const daily = await _cache; // Get the cached daily problem
  res.json(daily); // Return the daily problem as JSON
});

// Set the port for the server to listen on
const PORT = 8000;
app.listen(PORT, () => {
  console.log(`Server started on http://localhost:${PORT}`);
});
