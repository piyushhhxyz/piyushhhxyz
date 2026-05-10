const express = require("express");

const app = express();

app.get("/healthz", (req, res) => {
  res.status(200).json({ status: "ok" });
});

module.exports = app;
