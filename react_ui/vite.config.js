import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { sentryVitePlugin } from '@sentry/vite-plugin';

export default ({ mode }) => {
  return defineConfig({
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
    define: {
      'process.env.NODE_ENV': `"${mode}"`,
    },
    base: '',
    root: './src',
    publicDir: '../public',
    build: {
      outDir: '../build',
      sourcemap: true, // Generate source maps for Sentry
    },
  });
};
