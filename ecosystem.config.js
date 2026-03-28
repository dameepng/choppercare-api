const path = require("path");

const appDir = __dirname;
const logDir = path.join(appDir, "logs");

module.exports = {
  apps: [
    {
      name: "choppercare-api",
      script: "./venv/bin/gunicorn",
      args: "-w 2 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8001 --timeout 120",
      cwd: appDir,
      env: {
        PYTHONPATH: appDir,
        PYTHONUNBUFFERED: "1",
      },
      error_file: path.join(logDir, "pm2-error.log"),
      out_file: path.join(logDir, "pm2-out.log"),
      log_date_format: "YYYY-MM-DD HH:mm:ss",
      max_memory_restart: "500M",
      restart_delay: 3000,
      autorestart: true,
    },
  ],
};
