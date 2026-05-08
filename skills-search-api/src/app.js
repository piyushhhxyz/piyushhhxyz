const express = require('express');
const skillsRoutes = require('./routes/skills');
const errorHandler = require('./middleware/errorHandler');

const app = express();

app.use(express.json());

app.use('/api/skills', skillsRoutes);

// 404 handler
app.use((req, res, next) => {
  const err = new Error('Not found');
  err.status = 404;
  next(err);
});

// Error handler
app.use(errorHandler);

module.exports = app;
