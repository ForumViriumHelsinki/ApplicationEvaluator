/**
 * Vitest setup file
 * Runs before each test file
 */
import '@testing-library/jest-dom';

// Clean up after each test
afterEach(() => {
  // Clear all mocks
  vi.clearAllMocks();
});
