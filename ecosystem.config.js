module.exports = {
  apps: [
    {
      name: "choppercare-api",
      script: "venv/bin/gunicorn",
      args: "-w 2 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8001 --timeout 120",
      cwd: "/var/www/choppercare-api",
      env: {
        PYTHONPATH: "/var/www/choppercare-api",
        PYTHONUNBUFFERED: "1",
      },
      error_file: "/var/log/pm2/choppercare-api-error.log",
      out_file: "/var/log/pm2/choppercare-api-out.log",
      log_date_format: "YYYY-MM-DD HH:mm:ss",
      max_memory_restart: "500M",
      restart_delay: 3000,
      autorestart: true,
    },
  ],
};
