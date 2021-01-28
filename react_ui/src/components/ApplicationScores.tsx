import React from 'react';
import _ from 'lodash';
// @ts-ignore
import RadarChart from 'react-svg-radar-chart';
import 'react-svg-radar-chart/build/css/index.css'

import CriterionGroupComponent from "components/CriterionGroup";
import {Application, ApplicationRound, CriterionGroup} from "components/types";
import Modal from "util_components/bootstrap/Modal";
import {username} from "components/utils";

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

    const rootGroups = applicationRound.criterion_groups.filter(g => !g.parent);
    const thresholdGroups = applicationRound.criterion_groups.filter(g => g.threshold);

    return <div className="d-flex" key={application.name}>
      <div style={{width: 200, marginBottom: -64}}>
        {application.scores.length > 0 &&
        <RadarChart data={this.plotData()} size={200}
                    captions={this.plotCaptions()}
                    options={this.plotOptions()}/>
        }
      </div>

      <div className="flex-grow-1 flex-shrink-1 pt-5">
        <a onClick={() => this.setState({expanded: !this.state.expanded})}>
          <h5 className="text-primary mb-1">{application.name}</h5>
          {application.scores.length}/{applicationRound.criteria.length} scores
          {application.score && <>
            ,{' '}
            <strong>{application.score.toPrecision(2)}</strong> overall.<br/>
            {thresholdGroups.map(group => {
              const score = application.groupScores[group.id];
              return (score != null) && <span className="mr-2" key={group.name}>
                {group.name.split(' ')[0]}{' '}
                <span className={score < group.threshold ? 'text-danger font-weight-bold' : ''}>
                  {score.toPrecision(2)}
                </span>
              </span>
            })}
            <br/>
            Evaluated by {_.uniq(application.scores.map(s => username(s.evaluator))).join(', ')}
          </>}
        </a>
      </div>

      {expanded &&
      <Modal onClose={() => this.setState({expanded: false})} title={application.name}>
        {rootGroups.map(group =>
          <CriterionGroupComponent allGroups={applicationRound.criterion_groups} application={application}
                                   criteria={applicationRound.criteria} group={group} key={group.name}/>
        )}
        <div className="m-2">
          <button className="btn btn-block btn-secondary"
                  onClick={() => this.setState({expanded: false})}>Done
          </button>
        </div>
      </Modal>
      }
    </div>;
  }

  private shortName(group: CriterionGroup) {
    return (group.name.match(/^[\w\.]+/) || '')[0];
  }

  plotData() {
    const {applicationRound, application} = this.props;
    const thresholdGroups = applicationRound.criterion_groups.filter(g => g.threshold);
    if (!application.groupScores) return [];

    const data = Object.fromEntries(thresholdGroups.map(g =>
      [g.id, (application.groupScores[g.id] || 1) / 10]));

    return [{data: data, meta: {class: 'fill-secondary stroke-secondary'}}];
  }

  plotCaptions() {
    const {applicationRound, application} = this.props;
    const thresholdGroups = applicationRound.criterion_groups.filter(g => g.threshold);
    if (!application.groupScores) return {};

    return Object.fromEntries(thresholdGroups.map(g => [g.id, this.shortName(g)]));
  }

  plotOptions() {
    const {applicationRound, application} = this.props;
    const thresholdGroups = applicationRound.criterion_groups.filter(g => g.threshold);
    const thresholds = Object.fromEntries(thresholdGroups.map(g => [g.id, g.threshold]));

    return {
      captionMargin: 128,
      scales: 5,
      captionProps: ({key}: any) => {
        const score = application.groupScores[key];
        const groupIndex = thresholdGroups.findIndex(g => g.id == key);

        // Anchor captions on the right side of the plot to the start & on the left
        // to the end so they are rendered symmetrically around the outer circle:
        const textAnchor = groupIndex < thresholdGroups.length / 2 ? 'start' : 'end';

        return score == null ?
          {textAnchor, fill: '#ccc', class: 'chart-caption'}
          : score < thresholds[key] ?
            {fontWeight: 'bold', textAnchor, class: 'chart-caption fill-danger'}
            : {textAnchor, class: 'chart-caption'};
      },
    };
  }
}
