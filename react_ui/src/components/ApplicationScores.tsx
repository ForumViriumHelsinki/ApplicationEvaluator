import React from 'react';
import _ from 'lodash';
// @ts-ignore
import RadarChart from 'react-svg-radar-chart';
import 'react-svg-radar-chart/build/css/index.css'

import CriterionGroupComponent from "components/CriterionGroup";
import {AppContext, Application, ApplicationRound} from "components/types";
import Modal from "util_components/bootstrap/Modal";
import {organizationColor, username} from "components/utils";
import ApplicationScoresTable from "components/ApplicationScoresTable";


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
  static contextType = AppContext;

  render() {
    const {application, applicationRound} = this.props;
    const {expanded} = this.state;
    const {user} = this.context;

    const rootGroups = applicationRound.criterion_groups.filter(g => !g.parent);

    return <div className="mt-4 pb-4">
      <div className="d-flex">
        <div style={{width: 200, marginBottom: -48, marginTop: -38}} className="flex-shrink-0">
          {application.scores.length > 0 &&
          <RadarChart data={this.plotData()} size={200}
                      captions={this.plotCaptions()}
                      options={this.plotOptions()}/>
          }
        </div>

        <div className="flex-grow-1 flex-shrink-1">
          <a onClick={() => this.setState({expanded: !this.state.expanded})}>
            <h5 className="text-primary mb-1">{application.name}</h5>
          </a>
          <div className="mb-1">
            {application.evaluating_organizations.map(o =>
              <span className={`mr-2 small`} style={{color: this.organizationColor(o)}}
                    key={o}>{o}</span>
            )}
          </div>
          {application.score != null &&
          <><strong>{(application.score * 10).toPrecision(2)} / 100</strong> overall from </>}
          {application.scores.length}/{applicationRound.criteria.length} scores.
          {application.score != null && <>
            <br/>
            Evaluated by {_.uniq(application.scores.map(s => username(s.evaluator))).join(', ')}.
          </>}
        </div>
      </div>

      {application.score != null &&
      <div className="pl-4 pr-4">
        <ApplicationScoresTable application={application} applicationRound={applicationRound}/>
      </div>
      }

      {expanded &&
      <Modal onClose={() => this.setState({expanded: false})} title={application.name}>
        {application.attachments.length > 0 &&
        <div className="m-2">
          <h5 className="text-primary">Application attachments</h5>
          <div className="ml-2">
            {application.attachments.map(({attachment, name}) =>
              <a href={attachment} target='_blank' className="d-block text-secondary" key={attachment}>{name}</a>
            )}
          </div>
        </div>
        }
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

  plotData() {
    const {applicationRound, application} = this.props;
    const thresholdGroups = applicationRound.criterion_groups.filter(g => g.threshold);
    if (!application.groupScores) return [];

    const data = (groupScores: any) => Object.fromEntries(thresholdGroups.map(g =>
      [g.id, (groupScores[g.id] || 1) / 10]));

    if (Object.keys(application.scoresByOrganization).length < 2)
      return [{data: data(application.groupScores), meta: {color: organizationColor('total')}}];
    else return Object.entries(application.scoresByOrganization).map(([org, {groupScores}]) =>
      ({data: data(groupScores), meta: {color: organizationColor(org)}})
    );
  }

  plotCaptions() {
    const {applicationRound, application} = this.props;
    const thresholdGroups = applicationRound.criterion_groups.filter(g => g.threshold);
    if (!application.groupScores) return {};

    return Object.fromEntries(thresholdGroups.map(g => [g.id, g.abbr]));
  }

  plotOptions() {
    const {applicationRound, application} = this.props;
    const thresholdGroups = applicationRound.criterion_groups.filter(g => g.threshold);
    const thresholds = Object.fromEntries(thresholdGroups.map(g => [g.id, g.threshold]));

    return {
      captionMargin: 96,
      scales: 5,
      zoomDistance: 1.1,
      shapeProps: () => ({
        fillOpacity: 0.1, strokeWidth: 2
      }),
      captionProps: ({key}: any) => {
        const score = application.groupScores[key];
        const groupIndex = thresholdGroups.findIndex(g => g.id == key);

        // Anchor captions on the right side of the plot to the start & on the left
        // to the end so they are rendered symmetrically around the outer circle:
        const middle = thresholdGroups.length / 2;
        const textAnchor =
          groupIndex == 0 || groupIndex == middle ? 'middle'
            : groupIndex < middle ? 'start'
            : 'end';

        return score == null ?
          {textAnchor, fill: '#ccc', class: 'chart-caption'}
          : score < thresholds[key] ?
            {fontWeight: 'bold', textAnchor, class: 'chart-caption fill-danger'}
            : {textAnchor, class: 'chart-caption'};
      },
    };
  }

  organizationColor(o: string) {
    const {application} = this.props;
    return application.scoresByOrganization[o] ? 'black' : '#aaa';
  }
}
