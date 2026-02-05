export interface Settings {
  serverRoot: string;
  maxScore: number;
  finalScoreMultiplier: number;
  showScoresFromOtherUsers: boolean;
  allowSubmit: boolean;
}

// Default values used when window.__CONFIG__ is not available (e.g., in tests)
const defaults: Settings = {
  serverRoot: '',
  maxScore: 5,
  finalScoreMultiplier: 4,
  showScoresFromOtherUsers: true,
  allowSubmit: false,
};

// Declare the global config type
declare global {
  interface Window {
    __CONFIG__?: Partial<Settings>;
  }
}

// Runtime configuration from window.__CONFIG__ (injected via public/config.js)
// Falls back to defaults for any missing values
const settings: Settings = {
  ...defaults,
  ...window.__CONFIG__,
};

export default settings;
