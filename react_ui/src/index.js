import React from 'react';
import ReactDOM from 'react-dom';
import * as Sentry from '@sentry/browser';
// import * as serviceWorker from './serviceWorker';
import styles from './index.scss';
import ApplicationEvaluatorUI from "ApplicationEvaluatorUI"; // eslint-disable-line
import settings from './settings';

if (settings.sentryDsn)
  Sentry.init({dsn: settings.sentryDsn});

ReactDOM.render(<ApplicationEvaluatorUI/>, document.getElementById('root'));

// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: https://bit.ly/CRA-PWA
// serviceWorker.unregister();
