import React from "react";
import CenteredSpinner from "/util_components/bootstrap/CenteredSpinner";

export default class LoadScreen extends React.Component {
  render() {
    return <div className="container">
      <div className="jumbotron mt-5 p-0 bg-light shadow text-center">
        <div className="p-4 bg-primary mb-4">
          <img className="w-50" src="images/Space4Cities_logo.png" alt="logo"/>
        </div>
        <h3>FVH Application Evaluator</h3>
        <CenteredSpinner/>
      </div>
    </div>;
  }
}
