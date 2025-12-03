import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';

// Custom plugin to resolve absolute imports starting with '/' to src directory
const resolveAbsoluteImports = () => ({
  name: 'resolve-absolute-imports',
  resolveId(source: string) {
    if (source.startsWith('/') && !source.startsWith('//')) {
      return resolve(__dirname, 'src', source.slice(1));
    }
    return null;
  },
});

export default defineConfig({
  plugins: [react(), resolveAbsoluteImports()],
  test: {
    // Enable globals for compatibility with Jest-style tests
    globals: true,

    // Test environment (jsdom for DOM testing)
    environment: 'jsdom',

    // Setup files to run before tests
    setupFiles: ['./tests/setup.ts'],

    // Coverage configuration
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html', 'lcov'],
      exclude: [
        'node_modules/',
        'dist/',
        'build/',
        'tests/',
        '**/*.config.*',
        '**/*.d.ts',
        'src/index.jsx',
      ],
      thresholds: {
        lines: 80,
        functions: 80,
        branches: 80,
        statements: 80,
      },
    },

    // Watch mode exclusions
    watchExclude: ['**/node_modules/**', '**/dist/**', '**/build/**'],

    // Test timeout
    testTimeout: 10000,

    // Include/exclude patterns
    include: ['**/*.{test,spec}.{js,mjs,cjs,ts,mts,cts,jsx,tsx}'],
    exclude: ['node_modules', 'dist', 'build'],

    // Root directory for tests
    root: '.',
  },

  // Resolve aliases
  resolve: {
    alias: {
      '@': resolve(__dirname, './src'),
    },
  },
});
