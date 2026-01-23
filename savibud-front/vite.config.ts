import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA, VitePWAOptions } from "vite-plugin-pwa";
import tailwindcss from '@tailwindcss/vite'

const manifestForPlugIn: Partial<VitePWAOptions> = {
  registerType: 'autoUpdate',
  includeAssets: ['/assets/favicon.ico', "/img/sav.png", 'robots.txt'],
  manifest: {
    name: "Savibud",
    short_name: "Savibud",
    description: "Tool to help you manage your expenses, savings, budgets and more.",
    icons: [{
      src: '/android-chrome-192x192.png',
      sizes: '192x192',
      type: 'image/png',
      purpose: 'favicon'
    },
    {
      src: '/android-chrome-512x512.png',
      sizes: '512x512',
      type: 'image/png',
      purpose: 'favicon'
    },
    {
      src: 'assets/apple-touch-icon.png',
      sizes: '180x180',
      type: 'image/png',
      purpose: 'apple touch icon',
    },
    {
      purpose: "maskable",
      sizes: "192x192",
      src: "assets/maskable_icon_x192.png",
      type: "image/png"
    },
    {
      purpose: "maskable",
      sizes: "512x512",
      src: "assets/maskable_icon_x512.png",
      type: "image/png"
    }
    ],
    theme_color: '#201b5b',
    background_color: '#f0e7db',
    display: "standalone",
    scope: '/',
    start_url: "/",
    orientation: 'portrait'
  },
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
        target: 'http://localhost:14673',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''), // Removes /api before sending to backend
      },
    },
  },
})