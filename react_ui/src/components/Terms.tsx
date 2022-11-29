import React from 'react';
import Modal from "/util_components/bootstrap/Modal";

type TermsProps = {}

type TermsState = {showTerms: any}

const initialState: TermsState = {showTerms: false};

export default class Terms extends React.Component<TermsProps, TermsState> {
  state = initialState;

  render() {
    const {showTerms} = this.state;
    return <>
      <p>
        By using this website, you agree to
        our <a onClick={() => this.setState({showTerms: 'terms'})} className="clickable text-primary">
          Usage terms & privacy policy
        </a>.
      </p>
      {showTerms &&
        <Modal onClose={() => this.setState({showTerms: false})} title="">
          <iframe style={{height: 'calc(100vh - 270px)', width: '100%', border: 'none'}}
                  className="mt-2" src={`/${showTerms}.html`}/>
          <div className="p-2">
            <button className="btn btn-outline-primary btn-block"
                    onClick={() => this.setState({showTerms: false})}>
              Close
            </button>
          </div>
        </Modal>
      }
    </>;
  }
}
