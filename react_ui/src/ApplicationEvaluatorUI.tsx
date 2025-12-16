import React from "react";
import {
	Navigate,
	Route,
	HashRouter as Router,
	Routes,
	useParams,
} from "react-router-dom";

import sessionRequest, { logout } from "/sessionRequest";

import ApplicationRounds from "/components/ApplicationRounds";
import LoadScreen from "/components/LoadScreen";
import LoginScreen from "/components/LoginScreen";
import ResetPasswordScreen from "/components/ResetPasswordScreen";
import type { User } from "/components/types";
import Confirm from "/util_components/bootstrap/Confirm";
import NavBar from "/util_components/bootstrap/NavBar";

type UIState = {
	user?: User;
	dataFetched: boolean;
	showLogout?: boolean;
	sessionBroken?: boolean;
};

function ResetPassword() {
	const params = useParams<{ uid: string; token: string }>();
	return <ResetPasswordScreen uid={params.uid} token={params.token} />;
}

class ApplicationEvaluatorUI extends React.Component<object, UIState> {
	state: UIState = {
		user: undefined,
		dataFetched: false,
	};

	componentDidMount() {
		this.refreshUser();
	}

	refreshUser() {
		sessionRequest("/rest-auth/user/").then((response) => {
			if (response.status === 401)
				this.setState({ user: undefined, dataFetched: true });
			else
				response
					.json()
					.then((user) => this.setState({ user, dataFetched: true }));
		});
	}

	logout = () => logout().then(() => this.setState({ user: undefined }));

	request = (url: string, options: object = {}) => {
		return sessionRequest(url, options).then((response) => {
			if (response.status === 403) this.setState({ sessionBroken: true });
			return response;
		});
	};

	render() {
		const { user, dataFetched } = this.state;

		return (
			<Router>
				<Routes>
					<Route
						path="/login/"
						element={
							user ? (
								<Navigate to="/" replace />
							) : (
								<LoginScreen onLogin={() => this.refreshUser()} />
							)
						}
					/>
					<Route
						path="/resetPassword/:uid/:token"
						element={<ResetPassword />}
					/>
					<Route
						path="/"
						element={
							dataFetched ? (
								user ? (
									this.renderMain()
								) : (
									<Navigate to="/login/" replace />
								)
							) : (
								<LoadScreen />
							)
						}
					/>
				</Routes>
			</Router>
		);
	}

	renderMain() {
		const { showLogout, user, sessionBroken } = this.state;

		return (
			<>
				<NavBar
					onIconClick={() => this.setState({ showLogout: true })}
					icon="account_circle"
					iconText={user?.username || ""}
				>
					<h5 className="m-2">CommuniCity Application Evaluator</h5>
				</NavBar>
				<ApplicationRounds user={user as User} request={this.request} />
				{showLogout && (
					<Confirm
						title="Log out?"
						onClose={() => this.setState({ showLogout: false })}
						onConfirm={this.logout}
					/>
				)}
				{sessionBroken && (
					<Confirm
						title="It appears your session is expired. Please log in again to continue."
						onClose={() => this.setState({ sessionBroken: false })}
						onConfirm={this.logout}
					/>
				)}
			</>
		);
	}
}

export default ApplicationEvaluatorUI;
