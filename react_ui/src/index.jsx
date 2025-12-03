import '/init.js';
import React from 'react';
import ReactDOM from 'react-dom';
import * as Sentry from '@sentry/browser';
// import * as serviceWorker from './serviceWorker';
import styles from './index.scss';
import ApplicationEvaluatorUI from "/ApplicationEvaluatorUI"; // eslint-disable-line
import settings from './settings';

// Sentry DSN from environment variable (set via VITE_SENTRY_DSN)
const sentryDsn = import.meta.env.VITE_SENTRY_DSN;
if (sentryDsn) {
  Sentry.init({
    dsn: sentryDsn,
    environment: import.meta.env.MODE,
    release: import.meta.env.VITE_SENTRY_RELEASE,
    tracesSampleRate: import.meta.env.PROD ? 0.1 : 1.0,
  });
}

ReactDOM.render(<ApplicationEvaluatorUI/>, document.getElementById('root'));

// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: https://bit.ly/CRA-PWA
// serviceWorker.unregister();
