import React from 'react';
import _ from 'lodash';
// @ts-ignore
import RadarChart from 'react-svg-radar-chart';
import 'react-svg-radar-chart/build/css/index.css'

import CriterionGroupComponent from "/components/CriterionGroup";
import {AppContext, Application, ApplicationRound} from "/components/types";
import Modal from "/util_components/bootstrap/Modal";
import {organizationColor, slug, username, getTotalScore} from "/components/utils";
import ApplicationScoresTable from "/components/ApplicationScoresTable";
import ReactMarkdown from "react-markdown";
import ExportScoresWidget from "/components/ExportScoresWidget";
import settings from "/settings";
import ApplicationApproveWidget from "/components/ApplicationApproveWidget";


type ApplicationScoresProps = {
  application: Application,
  applicationRound: ApplicationRound,
  showEvaluators: boolean,
  showScores: boolean
}

type ApplicationScoresState = {
  expanded?: boolean,
  highlightOrganization?: string | null
}

const initialState: ApplicationScoresState = {};

export default class ApplicationScores extends React.Component<ApplicationScoresProps, ApplicationScoresState> {
  state = initialState;
  static contextType = AppContext;
  endHighlight: any = null;

  render() {
    const {application, applicationRound, showEvaluators, showScores} = this.props;
    const {expanded, highlightOrganization} = this.state;
    const {user} = this.context;

    const rootGroups = applicationRound.criterion_groups.filter(g => !g.parent);
    const thresholdGroups = applicationRound.criterion_groups.filter(g => g.threshold);
    const scoredCriteria = _.uniq(application.scores.map(s => s.criterion));

    const organizations = Object.keys(application.scoresByOrganization);
    const showOrganizations = showEvaluators && organizations.length > 1;
    const showPlot = showOrganizations && thresholdGroups.length > 1;

    const applicationAsRound = {...applicationRound, name: application.name, applications: [application]};

    const totalScore = getTotalScore(application);
    const maxScore = settings.maxScore * settings.finalScoreMultiplier;

    return <div className={`mt-4 pb-4 app-${application.id}`}>
      <div className="d-flex mr-4">
        {highlightOrganization &&
          <style>
            .app-{application.id} .org-shape {'{opacity: 0.2; transition: opacity 100ms;}'}
            .app-{application.id} .org-shape-{slug(highlightOrganization)} {'{opacity: 1}'}
          </style>
        }
        {thresholdGroups.length > 1 &&
          <div style={{width: 200, marginBottom: -48, marginTop: -38}} className="flex-shrink-0">
            {application.scores.length > 0 &&
              <RadarChart data={this.plotData()} size={200}
                      captions={this.plotCaptions()}
                      options={this.plotOptions()}/>
          }
        </div>
        }

        <div className={`flex-grow-1 flex-shrink-1 ${thresholdGroups.length < 2 ? 'ml-4' : ''}`}>
          <a onClick={() => this.setState({expanded: !this.state.expanded})}>
            <h5 className="text-primary mb-1">
              {application.name}
            </h5>
          </a>

          {showEvaluators &&
            <div className="mb-1">
              {application.evaluating_organizations.map(o =>
                <span className={`mr-2 small`} style={{color: this.organizationColor(o)}}
                      key={o}>{o}</span>
              )}
            </div>
          }

          {application.score != null ?
            showEvaluators ? <>
                <strong>{totalScore}/{maxScore}</strong>{' '}
                overall from {application.scores.length} scores for {scoredCriteria.length} criteria.
                <br/>
                Evaluated by {_.uniq(application.scores.map(s => username(s.evaluator))).join(', ')}.
              </>
              : <><strong>{totalScore}/{maxScore}</strong> overall score.</>
            : <>No scores given.</>
          }
        </div>

        <div className="flex-shrink-0 text-right">
          <button className="btn btn-outline-primary btn-sm btn-block mb-2"
                  onClick={() => this.setState({expanded: !this.state.expanded})}>
            {expanded ? 'Hide' : 'Show'} scores
          </button>
          <ApplicationApproveWidget className="btn btn-sm btn-block"
                                    application={application} applicationRound={applicationRound}/>
        </div>
      </div>

      {application.score != null &&
      <div className="pl-4 pr-4">
        <ApplicationScoresTable
          application={application} applicationRound={applicationRound} showEvaluators={showEvaluators}
          onOrganizationHover={this.highlightOrganization}/>
        {showPlot && <small>Move mouse over table to highlight organization in plot.</small>}
      </div>
      }

      {expanded &&
        <Modal onClose={() => this.setState({expanded: false})} title={application.name} className="modal-lg">
          {application.description && <>
            <h3 className="p-2 bg-primary text-white">Application information</h3>
            <ReactMarkdown linkTarget="_blank" className="m-2">{application.description}</ReactMarkdown>
          </>}
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

          <h3 className="mt-3 p-2 bg-primary text-white">Application evaluation</h3>
          {application.scores.length > 0 &&
            <div className="m-2"><ExportScoresWidget applicationRound={applicationAsRound}/></div>}
          {rootGroups.map(group =>
            <CriterionGroupComponent applicationRound={applicationRound} application={application}
                                     group={group} key={group.name} showScores={showScores}/>
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
    const {applicationRound, application, showEvaluators} = this.props;
    const thresholdGroups = applicationRound.criterion_groups.filter(g => g.threshold);
    if (!application.groupScores) return [];

    const data = (groupScores: any) => Object.fromEntries(thresholdGroups.map(g =>
      [g.id, (groupScores[g.id] || 1) / 10]));

    if (!showEvaluators || Object.keys(application.scoresByOrganization).length < 2)
      return [{
        data: data(application.groupScores),
        meta: {color: organizationColor('total')}
      }];

    else return Object.entries(application.scoresByOrganization).map(([org, {groupScores}]) =>
      ({data: data(groupScores), meta: {color: organizationColor(org), class: `org-shape org-shape-${slug(org)}`}})
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

  highlightOrganization = (highlightOrganization: string | null) => {
    this.setState({highlightOrganization});
    if (this.endHighlight) clearTimeout(this.endHighlight);
    this.endHighlight = setTimeout(() => this.setState({highlightOrganization: null}), 1000);
  };

  componentWillUnmount() {
    if (this.endHighlight) clearTimeout(this.endHighlight);
  }
}
