import {defineConfig} from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [react()],
    server: {
    host: '0.0.0.0'  // 这样设置会让服务器只监听 127.0.0.1 地址
  }
})
