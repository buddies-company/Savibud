import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA, VitePWAOptions } from "vite-plugin-pwa";
import tailwindcss from '@tailwindcss/vite'

const manifestForPlugIn: Partial<VitePWAOptions> = {
  registerType: 'autoUpdate',
  includeAssets: ['/assets/favicon.ico', "/img/sav.png", 'robots.txt'],
  manifest: false, // Use static manifest instead
  workbox: {
    runtimeCaching: [
      {
        urlPattern: ({ request }) => request.destination === 'document',
        handler: 'NetworkFirst',
      },
      {
        urlPattern: ({ request }) =>
          ['style', 'script', 'image'].includes(request.destination),
        handler: 'CacheFirst',
      },
      {
        urlPattern: /^https:\/\/jsonplaceholder\.typicode\.com\/posts/,
        handler: 'NetworkFirst',
        options: {
          cacheName: 'api-cache',
          expiration: {
            maxEntries: 50,
            maxAgeSeconds: 60 * 60 * 24, // 1 jour
          },
        },
      },
    ],
  },
}

export default defineConfig({
  plugins: [react(), VitePWA(manifestForPlugIn), tailwindcss(),],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8004',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''), // Removes /api before sending to backend
      },
    },
  },
})