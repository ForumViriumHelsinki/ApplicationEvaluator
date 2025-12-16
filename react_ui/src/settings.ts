import settingsJson from "./settings.json";

export interface Settings {
	serverRoot: string;
	maxScore: number;
	finalScoreMultiplier: number;
	showScoresFromOtherUsers: boolean;
	allowSubmit: boolean;
}

const settings: Settings = settingsJson;

export default settings;
