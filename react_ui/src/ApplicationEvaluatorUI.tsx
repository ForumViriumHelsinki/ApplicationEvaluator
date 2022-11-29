import React from 'react';
// @ts-ignore
import {HashRouter as Router, Route, Switch, useParams, Redirect} from "react-router-dom";

import sessionRequest, {logout} from "sessionRequest";

import LoginScreen from 'components/LoginScreen';
import LoadScreen from "components/LoadScreen";
import {User} from "components/types";
import ResetPasswordScreen from "components/ResetPasswordScreen";
import NavBar from "util_components/bootstrap/NavBar";
import Confirm from "util_components/bootstrap/Confirm";
import ApplicationRounds from "components/ApplicationRounds";

type UIState = {
  user?: User,
  dataFetched: boolean,
  showLogout?: boolean,
  sessionBroken?: boolean
}

class ApplicationEvaluatorUI extends React.Component<{}, UIState> {
  state: UIState = {
    user: undefined,
    dataFetched: false
  };

  componentDidMount() {
    this.refreshUser();
  }

  refreshUser() {
    sessionRequest('/rest-auth/user/').then(response => {
      if (response.status == 401) this.setState({user: undefined, dataFetched: true});
      else response.json().then(user => this.setState({user, dataFetched: true}));
    })
  }

  logout = () => logout().then(() => this.setState({user: undefined}));

  request = (url: string, options: any = {}) => {
    return sessionRequest(url, options).then(response => {
      if (response.status == 403) this.setState({sessionBroken: true});
      return response
    })
  };

  render() {
    const {user, dataFetched} = this.state;

    const ResetPassword = () => {
      const params = useParams();
      return <ResetPasswordScreen uid={params.uid} token={params.token}/>;
    };

    return <Router>
      <Switch>
        <Route path='/login/'>
          {user ? <Redirect to="" /> : <LoginScreen onLogin={() => this.refreshUser()}/>}
        </Route>
        <Route path='/resetPassword/:uid/:token'>
          <ResetPassword/>
        </Route>
        <Route exact path=''>
          {dataFetched
            ? user
              ? this.renderMain()
              : <Redirect to="/login/" />
            : <LoadScreen/>}
        </Route>
      </Switch>
    </Router>;
  }

  renderMain() {
    const {showLogout, user, sessionBroken} = this.state;

    return <>
      <NavBar onIconClick={() => this.setState({showLogout: true})}
              icon="account_circle"
              iconText={user?.username || ''}>
        <h5 className="m-2">FVH Application Evaluator</h5>
      </NavBar>
      <ApplicationRounds user={user as User} request={this.request}/>
      {showLogout &&
      <Confirm title="Log out?"
               onClose={() => this.setState({showLogout: false})}
               onConfirm={this.logout}/>
      }
      {sessionBroken &&
      <Confirm title="It appears your session is expired. Please log in again to continue."
               onClose={() => this.setState({sessionBroken: false})}
               onConfirm={this.logout}/>
      }
    </>;
  }
}

export default ApplicationEvaluatorUI;
