const app = require("./app");

const PORT = process.env.PORT || 3000;

const server = app.listen(PORT, () => {
  console.log(`Server listening on port ${PORT}`);
});

// Graceful shutdown
let shuttingDown = false;

function shutdown(signal) {
  if (shuttingDown) {
    console.log(`${signal} received again – already shutting down`);
    return;
  }
  shuttingDown = true;

  console.log(`${signal} received – shutting down`);
  server.close(() => {
    console.log("Server closed");
    process.exit(0);
  });

  // Force exit if server.close() hangs (e.g. keep-alive connections)
  setTimeout(() => {
    console.error("Forced shutdown after timeout");
    process.exit(1);
  }, 10_000).unref();
}

process.on("SIGTERM", () => shutdown("SIGTERM"));
process.on("SIGINT", () => shutdown("SIGINT"));

module.exports = server;
