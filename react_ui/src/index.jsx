import "/init.js";
import * as Sentry from "@sentry/react";
import ReactDOM from "react-dom";
import ApplicationEvaluatorUI from "/ApplicationEvaluatorUI"; // eslint-disable-line

// Sentry DSN from environment variable (set via VITE_SENTRY_DSN)
const sentryDsn = import.meta.env.VITE_SENTRY_DSN;
if (sentryDsn) {
	Sentry.init({
		dsn: sentryDsn,
		environment: import.meta.env.MODE,
		release: import.meta.env.VITE_SENTRY_RELEASE,
		integrations: [Sentry.browserTracingIntegration()],
		tracesSampleRate: import.meta.env.PROD ? 0.1 : 1.0,
	});
}

ReactDOM.render(<ApplicationEvaluatorUI />, document.getElementById("root"));

// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: https://bit.ly/CRA-PWA
// serviceWorker.unregister();
