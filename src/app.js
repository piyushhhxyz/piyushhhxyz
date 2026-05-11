const express = require("express");

const app = express();

// Simple request logger
app.use((req, _res, next) => {
  console.log(`${new Date().toISOString()} ${req.method} ${req.url}`);
  next();
});

// Health check endpoint
app.get("/healthz", (_req, res) => {
  res.status(200).json({
    status: "ok",
    uptime: process.uptime(),
  });
});

module.exports = app;
