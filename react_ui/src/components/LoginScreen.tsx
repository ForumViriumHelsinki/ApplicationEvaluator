import React from 'react';
import {loginUrl, registerUrl, passwordResetUrl} from "/urls";
import LoginForm from "/util_components/account/LoginForm";
import Terms from "/components/Terms";

type func = () => any;

type LoginScreenProps = { onLogin: func };

type LoginScreenState = {
  showTerms: boolean
};

export default class LoginScreen extends React.Component<LoginScreenProps, LoginScreenState> {
  state: LoginScreenState = {
    showTerms: false
  };

  render() {
    const {onLogin} = this.props;

    return (
      <div className="container mt-5 rounded trans-bg p-0">
        <div className="text-center p-4 bg-primary">
          <img className="w-50" src="images/CommuniCity-logo-blue.png" alt="logo"/>
        </div>
        <div className="p-4">
          <div className="text-center">
            <h3>FVH Application Evaluator</h3>
            <p className="lead text-primary">Sign in</p>
          </div>
          <LoginForm loginUrl={loginUrl} onLogin={onLogin} passwordResetUrl={passwordResetUrl}/>
          <Terms/>
        </div>
      </div>
    );
  }
}
