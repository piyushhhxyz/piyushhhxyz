const errorHandler = (err, req, res, next) => {
  const status = err.status || 500;
  let message = err.message;

  if (status >= 500) {
    console.error(`[${new Date().toISOString()}] ${req.method} ${req.originalUrl} →`, err);
  }

  if (process.env.NODE_ENV === 'production' && status === 500) {
    message = 'Internal server error';
  }

  res.status(status).json({
    error: {
      message,
      status
    }
  });
};

module.exports = errorHandler;
