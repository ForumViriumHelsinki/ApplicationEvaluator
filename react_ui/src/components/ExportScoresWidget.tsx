import React from 'react';
import {Application, ApplicationRound, Comment, Criterion, Score} from "/components/types";
import XLSX from 'xlsx';

type ExportScoresWidgetProps = {
  applicationRound: ApplicationRound
}

type ExportScoresWidgetState = {
  expanded?: boolean
}

const initialState: ExportScoresWidgetState = {};

export default class ExportScoresWidget extends React.Component<ExportScoresWidgetProps, ExportScoresWidgetState> {
  state = initialState;

  render() {
    const {} = this.props;
    const {expanded} = this.state;
    return <div className="dropdown mt-2">
      <button className="btn btn-compact btn-sm btn-outline-dark dropdown-toggle"
              onClick={() => this.setState({expanded: !expanded})}>
        Export scores
      </button>
      {expanded &&
      <div className="dropdown-menu show">
        <button className="dropdown-item" onClick={() => this.export('.xlsx')}>.xlsx</button>
        <button className="dropdown-item" onClick={() => this.export('.csv')}>.csv</button>
      </div>
      }
    </div>;
  }

  export(format: string) {
    const applicationRound = this.props.applicationRound;
    const {applications, name} = applicationRound;
    const criteria = Object.fromEntries(applicationRound.criteria.map(c => [c.id, c]));
    const groups = Object.fromEntries(applicationRound.criterion_groups.map(c => [c.id, c.name]));

    const columns = [
      {name: 'Application', value: (s: Score, a: Application) => a.name},
      {
        name: 'Criterion group', value: (s: Score | Comment, a: Application) =>
          groups[(s as Comment).criterion_group || criteria[(s as Score).criterion].group]
      },
      {name: 'Criterion', value: (s: Score, a: Application) => criteria[s.criterion]?.name},
      {name: 'Organization', value: (s: Score, a: Application) => s.evaluator.organization},
      {name: 'First name', value: (s: Score, a: Application) => s.evaluator.first_name},
      {name: 'Last name', value: (s: Score, a: Application) => s.evaluator.last_name},
      {name: 'Score', value: (s: Score, a: Application) => s.score},
      {name: 'Comment', value: (s: Comment, a: Application) => s.comment},
    ];

    const rows = [columns.map(c => c.name)];

    applications.forEach(a => {
      // @ts-ignore
      a.scores.forEach(s => rows.push(columns.map(c => c.value(s, a) as string)));
      // @ts-ignore
      a.comments.forEach(s => rows.push(columns.map(c => c.value(s, a) as string)));
    });
    const worksheet = XLSX.utils.aoa_to_sheet(rows);
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, "Scores");
    XLSX.writeFile(workbook, name + format);
  }
}
