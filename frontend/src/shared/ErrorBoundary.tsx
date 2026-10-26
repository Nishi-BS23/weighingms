import { Component, type ReactNode } from "react";

interface Props {
  children: ReactNode;
  onBack: () => void;
}

interface State {
  failed: boolean;
}

/** Keeps a broken screen from taking down the terminal; offers a way back (story 010). */
export class ErrorBoundary extends Component<Props, State> {
  state: State = { failed: false };

  static getDerivedStateFromError(): State {
    return { failed: true };
  }

  render(): ReactNode {
    if (!this.state.failed) return this.props.children;
    return (
      <div className="queue">
        <div className="message error" role="alert">
          Something went wrong on this screen.
          <button
            type="button"
            className="key"
            onClick={() => {
              this.setState({ failed: false });
              this.props.onBack();
            }}
          >
            Back to batch queue
          </button>
        </div>
      </div>
    );
  }
}
