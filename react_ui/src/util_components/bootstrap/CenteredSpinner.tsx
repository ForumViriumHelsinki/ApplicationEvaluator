import React from 'react';

export default class CenteredSpinner extends React.Component {
  render() {
    return (
      <div className="text-center p-3">
        <output className="spinner-border text-secondary" aria-live="polite">
          <span className="sr-only">Loading...</span>
        </output>
      </div>
    );
  }
}
