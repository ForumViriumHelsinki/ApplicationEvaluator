import type { ReactNode } from "react";
import React from "react";

type ModalBodyProps = {
	children?: ReactNode;
};

export class ModalBody extends React.Component<ModalBodyProps> {
	render() {
		return <div className="modal-body">{this.props.children}</div>;
	}
}

type Action = {
	label: string;
	action: () => void;
	color:
		| "primary"
		| "secondary"
		| "light"
		| "outline-primary"
		| "outline-secondary";
};

export class ModalActions extends React.Component<{ actions: Action[] }> {
	render() {
		return (
			<div className="modal-footer">
				{this.props.actions.map(({ label, action, color }) => (
					<button
						key={label}
						type="button"
						className={`btn btn-${color}`}
						onClick={action}
					>
						{label}
					</button>
				))}
			</div>
		);
	}
}

type ModalProps = {
	title: ReactNode;
	onClose: () => void;
	children?: ReactNode;
	className?: string;
	headerContent?: ReactNode;
};

export default class Modal extends React.Component<ModalProps> {
	static defaultProps = { className: "" };

	escFunction = (event: KeyboardEvent) => {
		if (event.keyCode === 27) this.props.onClose();
	};

	componentDidMount() {
		document.addEventListener("keydown", this.escFunction, false);
	}

	componentWillUnmount() {
		document.removeEventListener("keydown", this.escFunction, false);
	}

	render() {
		const { title, onClose, children, className, headerContent } = this.props;

		return (
			<>
				<div className="modal-backdrop show"> </div>
				<div
					className="modal show d-block"
					tabIndex={-1}
					role="dialog"
					onClick={onClose}
				>
					<div
						className={`modal-dialog ${className}`}
						role="document"
						onClick={(e) => e.stopPropagation()}
					>
						<div className="modal-content">
							{(title || headerContent) && (
								<div className="modal-header">
									{title && <h6 className="modal-title">{title}</h6>}
									{headerContent}
									{onClose && (
										<button
											type="button"
											className="close"
											aria-label="Close"
											onClick={onClose}
										>
											<span aria-hidden="true">&times;</span>
										</button>
									)}
								</div>
							)}
							<div
								style={{ maxHeight: "calc(100vh - 200px)", overflowY: "auto" }}
							>
								{children}
							</div>
						</div>
					</div>
				</div>
			</>
		);
	}
}
