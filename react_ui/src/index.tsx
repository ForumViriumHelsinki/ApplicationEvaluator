import "/init.js";
import * as Sentry from "@sentry/react";
import { createRoot } from "react-dom/client";
import ApplicationEvaluatorUI from "/ApplicationEvaluatorUI";

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

const container = document.getElementById("root");
if (!container) {
	throw new Error("Root element not found");
}

const root = createRoot(container);
root.render(<ApplicationEvaluatorUI />);
