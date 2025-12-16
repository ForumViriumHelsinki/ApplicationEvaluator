import { resolve } from 'node:path';
import { defineConfig, type ConfigEnv } from 'vite';
import react from '@vitejs/plugin-react';
import { sentryVitePlugin } from '@sentry/vite-plugin';

export default defineConfig(({ mode }: ConfigEnv) => ({
  plugins: [
    react(),
    // Sentry plugin for source maps (only in production builds when auth token is available)
    mode === 'production' &&
      process.env.SENTRY_AUTH_TOKEN &&
      sentryVitePlugin({
        org: process.env.SENTRY_ORG,
        project: process.env.SENTRY_PROJECT,
        authToken: process.env.SENTRY_AUTH_TOKEN,
        release: {
          name: process.env.VITE_SENTRY_RELEASE,
        },
        sourcemaps: {
          assets: '../build/**',
        },
        telemetry: false,
      }),
  ].filter(Boolean),
  resolve: {
    alias: {
      '/': resolve(__dirname, 'src'),
    },
  },
  define: {
    'process.env.NODE_ENV': JSON.stringify(mode),
  },
  base: '',
  root: './src',
  publicDir: '../public',
  build: {
    outDir: '../build',
    sourcemap: true,
    emptyOutDir: true,
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './setupTests.ts',
    css: true,
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'lcov'],
    },
  },
}));
