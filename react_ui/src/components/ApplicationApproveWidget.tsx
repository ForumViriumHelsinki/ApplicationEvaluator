import React from 'react';
import {Application, ApplicationRound} from "/components/types";
import {AppContext} from "/components/types";
import {approveApplicationUrl, unapproveApplicationUrl} from "/urls";
import sessionRequest from "/sessionRequest";

type ApplicationApproveWidgetProps = {
  application: Application,
  applicationRound: ApplicationRound,
  className: string
}

type ApplicationApproveWidgetState = {}

const initialState: ApplicationApproveWidgetState = {};

export default class ApplicationApproveWidget extends React.Component<ApplicationApproveWidgetProps, ApplicationApproveWidgetState> {
  state = initialState;
  static contextType = AppContext;
  static defaultProps = {
    className: "btn btn-sm"
  }

  render() {
    const {application, applicationRound, className} = this.props;
    const {} = this.state;
    const {user} = this.context;
    const submitted = applicationRound.submitted_organizations.length > 0;
    if (!(user.is_superuser && submitted)) return null;

    return application.approved ?
      <button className={className + " btn-success"} onClick={this.unapprove}>
        Approved
      </button>
      :
      <button className={className + " btn-outline-success"} onClick={this.approve}>
        Approve
      </button>;
  }

  updateAction = (url: string) => {
    const {updateApplication} = this.context;
    sessionRequest(url, {method: 'post'})
      .then((response) => {
        if (response.ok) {
          response.json().then((data) => updateApplication(data));
        }
      })
  }

  approve = () => this.updateAction(approveApplicationUrl(this.props.application.id));

  unapprove = () => this.updateAction(unapproveApplicationUrl(this.props.application.id));
}
