import React, {FocusEvent} from 'react';
import {AppContext, Application, Criterion} from "components/types";
import Icon from "util_components/bootstrap/Icon";
import ConfirmButton from "util_components/bootstrap/ConfirmButton";
import sessionRequest from "sessionRequest";
import {scoresUrl, scoreUrl} from "urls";
import {username} from "components/utils";

type CriterionScoreProps = {
  criterion: Criterion,
  application: Application
}

type CriterionScoreState = {
  changed?: boolean
}

const initialState: CriterionScoreState = {};

export default class CriterionScore extends React.Component<CriterionScoreProps, CriterionScoreState> {
  state = initialState;
  static contextType = AppContext;

  render() {
    const {criterion, application} = this.props;
    const {changed} = this.state;
    const {user} = this.context;

    const score = this.getScore();

    return <div className="ml-2 mb-2">
      {criterion.name}:
      {(score && (score.evaluator.id != user.id)) ?
        <div><strong>{score.score}</strong> (by {username(score.evaluator)})</div>
      : score ?
        <div>
          <strong>{score.score}</strong> (by {username(score.evaluator)})
          <ConfirmButton className="btn-light btn-sm text-danger p-1" confirm="Delete score?"
                         onClick={this.deleteScore}>
            <Icon icon="clear"/>
          </ConfirmButton>
        </div>
      : <div className="form-inline">
          <input type="number" min="0" max="10" className="form-control form-control-sm"
                 onBlur={this.saveScore}
                 onChange={() => this.setState({changed: true})}/>{' '}
            {changed && <button className="btn btn-sm btn-outline-primary ml-2">Save</button>}
        </div>
      }
    </div>;
  }

  getScore() {
    const {criterion, application} = this.props;
    return application.scores.find(s => s.criterion == criterion.id);
  }

  saveScore = (e: FocusEvent<HTMLInputElement>) => {
    const {application, criterion} = this.props;
    const {reloadApplication} = this.context;
    const value = Number(e.target.value);
    if (!e.target.value || value > 10 || value < 0) return;
    const data = {application: application.id, criterion: criterion.id, score: value};
    sessionRequest(scoresUrl, {method: 'POST', data}).then(response => {
      if (response.status < 300) {
        this.setState({changed: false});
        reloadApplication(application.id);
      }
    })
  };

  deleteScore = () => {
    const {application} = this.props;
    const {reloadApplication} = this.context;
    const score = this.getScore();
    if (!score) return;
    sessionRequest(scoreUrl(score.id), {method: 'DELETE'}).then(response => {
      if (response.status < 300) reloadApplication(application.id);
    })
  }
}
