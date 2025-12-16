/// <reference types="vite/client" />

interface ImportMetaEnv {
	readonly VITE_SENTRY_DSN: string;
	readonly VITE_SENTRY_RELEASE: string;
	readonly MODE: string;
	readonly PROD: boolean;
	readonly DEV: boolean;
}

interface ImportMeta {
	readonly env: ImportMetaEnv;
}
