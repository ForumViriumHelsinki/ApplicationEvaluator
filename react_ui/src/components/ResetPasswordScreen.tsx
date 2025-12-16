import React from 'react';
import Terms from '/components/Terms';
import { changePasswordUrl } from '/urls';
import ResetPasswordForm from '/util_components/account/ResetPasswordForm';

type ResetPasswordScreenProps = {
  uid: string;
  token: string;
};

type ResetPasswordScreenState = {};

export default class ResetPasswordScreen extends React.Component<
  ResetPasswordScreenProps,
  ResetPasswordScreenState
> {
  state: ResetPasswordScreenState = {};

  render() {
    const { uid, token } = this.props;
    return (
      <div className="container mt-5 rounded trans-bg p-0">
        <div className="text-center p-4 bg-primary">
          <img className="w-50" src="images/CommuniCity-logo-blue.png" alt="logo" />
        </div>
        <div className="p-4">
          <div className="text-center">
            <h3>FVH Application Evaluator</h3>
            <p className="lead">Reset password</p>
          </div>
          <ResetPasswordForm changePasswordUrl={changePasswordUrl} token={token} uid={uid} />
          <Terms />
        </div>
      </div>
    );
  }
}
