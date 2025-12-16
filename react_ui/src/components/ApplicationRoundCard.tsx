import _ from "lodash";
import React from "react";
import ReactMarkdown from "react-markdown";
import ApplicationScores from "/components/ApplicationScores";
import ExportScoresWidget from "/components/ExportScoresWidget";
import { AppContext, type ApplicationRound } from "/components/types";
import sessionRequest from "/sessionRequest";
import settings from "/settings";
import { submitApplicationRoundUrl } from "/urls";
import ConfirmButton from "/util_components/bootstrap/ConfirmButton";
import Icon from "/util_components/bootstrap/Icon";

type ApplicationRoundCardProps = {
	applicationRound: ApplicationRound;
};

type AppOrder = "name" | "score" | "unevaluated";

type ApplicationRoundCardState = {
	order: AppOrder;
	showEvaluators: boolean;
	showScores: boolean;
	expanded?: boolean;
};

const initialState: ApplicationRoundCardState = {
	order: "name",
	showEvaluators: true,
	showScores: settings.showScoresFromOtherUsers,
};

export default class ApplicationRoundCard extends React.Component<
	ApplicationRoundCardProps,
	ApplicationRoundCardState
> {
	state = initialState;
	static contextType = AppContext;

	render() {
		const { applicationRound } = this.props;
		const { user } = this.context;
		const { showEvaluators, expanded } = this.state;
		const scoredApps = applicationRound.applications.filter((a) => a.scored);
		const partialApps = applicationRound.applications.filter(
			(a) => a.scores.length > 0,
		);
		const submitted = applicationRound.submitted_organizations.includes(
			user.organization,
		);

		// When scoring model is based on single evaluators, showing the evaluators in itself will show the scores so combine these:
		const showScores =
			applicationRound.scoring_model === "Evaluators average"
				? showEvaluators
				: this.state.showScores;

		const uniqueEvaluators = _.uniq(
			_.flatten(
				applicationRound.applications.map((a) =>
					a.scores.map((s) => s.evaluator),
				),
			),
		);

		const OrderBtn = ({ order, label }: { order: AppOrder; label: string }) => (
			<>
				{" "}
				<button
					className="btn btn-sm btn-outline-secondary rounded-pill"
					onClick={() => this.setState({ order })}
				>
					{label}
				</button>
			</>
		);

		return (
			<div className="container mt-4 mb-3 rounded trans-bg pl-0 pr-0 pt-4 pb-4">
				<div className="pl-4 pr-4">
					<div>
						<h3
							className="clickable text-primary mb-4"
							onClick={() => this.setState({ expanded: !expanded })}
						>
							{applicationRound.name}
						</h3>
						{submitted && (
							<span className="badge badge-pill badge-success small align-text-bottom">
								<Icon icon="done" className="font-size-base" /> Submitted
							</span>
						)}
					</div>
					{applicationRound.description && (
						<ReactMarkdown linkTarget="_blank">
							{applicationRound.description}
						</ReactMarkdown>
					)}
					{applicationRound.attachments.length > 0 && (
						<div className="mt-2">
							Documents:
							{applicationRound.attachments.map(({ attachment, name }) => (
								<a
									href={attachment}
									target="_blank"
									className="text-secondary ml-2"
									key={attachment}
									rel="noreferrer"
								>
									{name}
								</a>
							))}
						</div>
					)}
					{scoredApps.length}/{applicationRound.applications.length}{" "}
					applications evaluated
					{scoredApps.length > 0 && (
						<ExportScoresWidget {...{ applicationRound }} />
					)}
					{expanded &&
						settings.allowSubmit &&
						!submitted &&
						partialApps.length === applicationRound.applications.length && (
							<ConfirmButton
								onClick={this.submitScores}
								className="btn btn-outline-success btn-block mt-2 mb-3"
								confirm={
									<>
										Submit all {applicationRound.name} scores for{" "}
										{user.organization}? Scores cannot be changed after
										submitting.
										<div className="mt-2">
											{scoredApps.length}/{applicationRound.applications.length}{" "}
											applications completely evaluated
											{scoredApps.length <
												applicationRound.applications.length && (
												<>
													, {partialApps.length - scoredApps.length} partially.
												</>
											)}
										</div>
									</>
								}
							>
								<Icon icon="lock" /> Submit scores for {user.organization}
							</ConfirmButton>
						)}
					<div className="mt-2 mb-3">
						<button
							className="btn btn-outline-primary btn-sm"
							onClick={() => this.setState({ expanded: !expanded })}
						>
							{expanded ? "Hide" : "Show"} applications
						</button>
					</div>
					{expanded && (
						<div className="mt-2">
							<div className="mr-3 d-inline-block">
								Order by:
								<OrderBtn label="Name" order="name" />
								<OrderBtn label="Score" order="score" />
								<OrderBtn label="Unevaluated" order="unevaluated" />
							</div>
							<div
								className="form-check d-inline-block mr-3"
								onClick={() =>
									this.setState({ showEvaluators: !showEvaluators })
								}
							>
								<input
									className="form-check-input"
									type="checkbox"
									checked={showEvaluators}
								/>
								<label className="form-check-label">Show evaluators</label>
							</div>
							{settings.showScoresFromOtherUsers &&
								!submitted &&
								uniqueEvaluators.length > 1 &&
								applicationRound.scoring_model !== "Evaluators average" && (
									<div
										className="form-check d-inline-block mr-3"
										onClick={() => this.setState({ showScores: !showScores })}
									>
										<input
											className="form-check-input"
											type="checkbox"
											checked={showScores}
										/>
										<label className="form-check-label">
											Show scores from other evaluators
										</label>
									</div>
								)}
						</div>
					)}
				</div>
				{expanded &&
					this.getApplications().map((app) => (
						<ApplicationScores
							application={app}
							applicationRound={applicationRound}
							key={app.name}
							showEvaluators={showEvaluators}
							showScores={showScores || submitted}
						/>
					))}
			</div>
		);
	}

	getApplications() {
		const { order } = this.state;
		const { applicationRound } = this.props;
		if (order === "name") return applicationRound.applications;

		const apps = [...applicationRound.applications];

		if (order === "unevaluated")
			apps.sort((a, b) => a.scores.length - b.scores.length);
		else if (order === "score")
			apps.sort((a, b) => (b.score || 0) - (a.score || 0));
		return apps;
	}

	submitScores = () => {
		const { applicationRound } = this.props;
		const { loadRounds } = this.context;
		sessionRequest(submitApplicationRoundUrl(applicationRound.id), {
			method: "POST",
		}).then((response) => {
			if (response.status < 300) loadRounds();
		});
	};
}
