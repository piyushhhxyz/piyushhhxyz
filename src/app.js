const express = require("express");

const app = express();

app.get("/healthz", (_req, res) => {
  res.status(200).json({ status: "ok" });
});

app.all("/healthz", (_req, res) => {
  res.status(405).set("Allow", "GET, HEAD").json({ error: "Method Not Allowed" });
});

module.exports = app;
