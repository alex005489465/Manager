module.exports = {
  apps: [
    {
      name: 'bench-framework',
      script: 'src/index.js',
      instances: 'max', // 使用所有 CPU 核心
      exec_mode: 'cluster', // 集群模式

      // 環境變數
      env: {
        NODE_ENV: 'development',
        PORT: 3000,
      },
      env_production: {
        NODE_ENV: 'production',
        PORT: 3000,
      },

      // PM2 設定
      watch: false,
      ignore_watch: ['node_modules', 'logs', 'prisma/migrations'],
      max_memory_restart: '500M',
      restart_delay: 4000,

      // 日誌設定
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      error_file: 'logs/err.log',
      out_file: 'logs/out.log',
      log_file: 'logs/combined.log',
      merge_logs: true,

      // 進階設定
      min_uptime: '10s',
      max_restarts: 10,
      autorestart: true,

      // 健康檢查
      health_check_grace_period: 3000,

      // 性能監控
      pmx: true,

      // 集群設定
      instance_var: 'INSTANCE_ID',

      // 進程設定
      kill_timeout: 5000,
      listen_timeout: 3000,

      // 資源限制
      max_memory_restart: '1G',

      // 自動重啟條件
      cron_restart: '0 2 * * *', // 每天凌晨 2 點重啟

      // 追蹤設定
      source_map_support: true,

      // 環境特定設定
      node_args: '--max-old-space-size=1024',

      // 錯誤處理
      exp_backoff_restart_delay: 100,
    }
  ],

  // 部署配置
  deploy: {
    production: {
      user: 'ec2-user',
      host: ['bench-1'],
      ref: 'origin/main',
      repo: 'git@github.com:your-repo/bench-framework.git',
      path: '/home/ec2-user/bench-framework',
      'post-deploy': 'npm install && npm run build && npm run db:deploy && pm2 reload ecosystem.config.js --env production',
      'pre-setup': 'apt update -y; apt install nodejs npm git -y'
    }
  }
};