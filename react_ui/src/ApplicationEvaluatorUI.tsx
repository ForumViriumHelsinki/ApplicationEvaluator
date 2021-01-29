import React from 'react';
// @ts-ignore
import {HashRouter as Router, Route, Switch, useParams, Redirect} from "react-router-dom";

import sessionRequest, {logout} from "sessionRequest";

import LoginScreen from 'components/LoginScreen';
import LoadScreen from "components/LoadScreen";
import {AppContext, User} from "components/types";
import ResetPasswordScreen from "components/ResetPasswordScreen";
import NavBar from "util_components/bootstrap/NavBar";
import Confirm from "util_components/bootstrap/Confirm";
import ApplicationRounds from "components/ApplicationRounds";

type UIState = {
  user?: User,
  dataFetched: boolean,
  showLogout?: boolean
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

  logout = () => {
    sessionRequest('/rest-auth/logout/', {method: 'POST'}).then(response => {
      logout();
      this.setState({user: undefined});
    });
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
    const {showLogout, user} = this.state;

    return <>
      <NavBar onIconClick={() => this.setState({showLogout: true})}
              icon="account_circle"
              iconText={user?.username || ''}>
        <h5 className="m-2">FVH Application Evaluator</h5>
      </NavBar>
      <div className="container mt-4 mb-5 rounded trans-bg pl-0 pr-0">
        <ApplicationRounds user={user as User}/>
      </div>
      <p className="text-white text-center">
        Background: Selkämerenpuisto park, Helsinki. (c) City of Helsinki, photo by Jussi Hellsten
      </p>
      {showLogout &&
      <Confirm title="Log out?"
               onClose={() => this.setState({showLogout: false})}
               onConfirm={this.logout}/>
      }
    </>;
  }
}

export default ApplicationEvaluatorUI;
