import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
      '@components': path.resolve(__dirname, 'src/components'),
      '@pages': path.resolve(__dirname, 'src/pages'),
      '@services': path.resolve(__dirname, 'src/services'),
      '@modules': path.resolve(__dirname, 'src/modules'),
      '@types': path.resolve(__dirname, 'src/types'),
      '@utils': path.resolve(__dirname, 'src/utils'),
      '@hooks': path.resolve(__dirname, 'src/hooks'),
      '@context': path.resolve(__dirname, 'src/context'),
      '@styles': path.resolve(__dirname, 'src/styles'),
      '@routes': path.resolve(__dirname, 'src/routes'),
      '@router': path.resolve(__dirname, 'src/router'),
      '@store': path.resolve(__dirname, 'src/store'),
      '@layouts': path.resolve(__dirname, 'src/layouts')
    }
  },
  server: {
    port: 3000,
    host: '0.0.0.0',
    strictPort: true, // 強制使用端口3000，不會自動切換到其他端口
    hmr: {
      port: 3001, // 使用不同端口避免衝突
      host: 'localhost' // 改用 localhost 而不是 0.0.0.0
    },
    watch: {
      usePolling: true,
      interval: 1000
    },
    proxy: {
      '/api': {
        target: 'http://java-dev:8080',
        changeOrigin: true,
        secure: false
      }
    }
  },
  build: {
    target: 'baseline-widely-available', // Vite 7新預設
    outDir: 'dist',
    sourcemap: true
  }
})