import React from 'react';

export class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('[ErrorBoundary caught error]:', error, errorInfo);
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null });
    window.location.reload();
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-[#f8fafc] flex items-center justify-center p-6 text-[#0f2931]">
          <div className="bg-white rounded-3xl p-8 border border-[#c8d8e4] shadow-2xl max-w-lg w-full text-center space-y-4">
            <div className="w-14 h-14 bg-amber-500/10 text-amber-600 rounded-full flex items-center justify-center mx-auto text-2xl font-bold">
              ⚠️
            </div>
            <h2 className="text-xl font-extrabold text-[#0f2931]">Application Interface Error</h2>
            <p className="text-xs text-[#4d6e78]">
              An unexpected render error occurred in this view. The system caught the exception automatically.
            </p>
            {this.state.error?.message && (
              <div className="bg-[#f2f2f2] p-3 rounded-xl font-mono text-[11px] text-red-600 overflow-x-auto text-left">
                {this.state.error.message}
              </div>
            )}
            <button
              onClick={this.handleReset}
              className="px-6 py-3 bg-[#52ab98] hover:bg-[#3e8f7e] text-white rounded-full font-bold text-xs shadow-lg transition-all"
            >
              Reload Page
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
