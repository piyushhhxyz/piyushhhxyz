const app = require("./app");

const PORT = process.env.PORT || 3000;

const server = app.listen(PORT, () => {
  console.log(`Server listening on port ${PORT}`);
});

function shutdown(signal) {
  console.log(`${signal} received – shutting down`);
  server.close(() => {
    console.log("Server closed");
    process.exit(0);
  });
  setTimeout(() => {
    console.error("Forcefully shutting down");
    process.exit(1);
  }, 10_000).unref();
}

process.on("SIGTERM", () => shutdown("SIGTERM"));
process.on("SIGINT", () => shutdown("SIGINT"));

module.exports = server;
