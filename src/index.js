const app = require("./app");

const PORT = process.env.PORT || 3000;
const SHUTDOWN_TIMEOUT_MS = 10_000;

const server = app.listen(PORT, () => {
  console.log(`Server listening on port ${PORT}`);
});

function shutdown(signal) {
  console.log(`${signal} received, shutting down gracefully`);

  server.close(() => {
    console.log("Server closed");
    process.exit(0);
  });

  // Stop accepting new connections on idle keep-alive sockets immediately
  server.closeIdleConnections?.();

  // Force exit if connections refuse to drain within the timeout
  setTimeout(() => {
    console.error("Forcing shutdown after timeout");
    server.closeAllConnections?.();
    process.exit(1);
  }, SHUTDOWN_TIMEOUT_MS).unref();
}

process.on("SIGTERM", () => shutdown("SIGTERM"));
process.on("SIGINT", () => shutdown("SIGINT"));

module.exports = server;
