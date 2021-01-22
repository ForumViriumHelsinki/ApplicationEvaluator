import React from 'react';
import CriterionGroupComponent from "components/CriterionGroup";
import {Application, ApplicationRound} from "components/types";
import Modal from "util_components/bootstrap/Modal";
import {averageScore} from "components/utils";

type ApplicationScoresProps = {
  application: Application,
  applicationRound: ApplicationRound
}

type ApplicationScoresState = {
  expanded?: boolean
}

const initialState: ApplicationScoresState = {};

export default class ApplicationScores extends React.Component<ApplicationScoresProps, ApplicationScoresState> {
  state = initialState;

  render() {
    const {application, applicationRound} = this.props;
    const {expanded} = this.state;

    return <div className="mt-3 ml-4" key={application.name}>
      <a onClick={() => this.setState({expanded: !this.state.expanded})}>
        <h5 className="text-primary mb-1">{application.name}</h5>
        {application.scores.length}/{applicationRound.criteria.length} scores,{' '}
        <strong>{averageScore(application).toPrecision(2)}</strong> average.
      </a>
      {expanded &&
        <Modal onClose={() => this.setState({expanded: false})} title={application.name}>
          {applicationRound.criterion_groups.filter(g => !g.parent).map(group =>
            <CriterionGroupComponent allGroups={applicationRound.criterion_groups} application={application}
                                     criteria={applicationRound.criteria} group={group} key={group.name}/>
          )}
          <div className="m-2">
            <button className="btn btn-block btn-secondary"
                    onClick={() => this.setState({expanded: false})}>Done</button>
          </div>
        </Modal>
      }
    </div>;
  }
}
