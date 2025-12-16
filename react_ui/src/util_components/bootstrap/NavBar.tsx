import React from "react";
import Icon from "/util_components/bootstrap/Icon";

type NavBarProps = { icon: string; iconText: string; onIconClick?: () => any };

export default class NavBar extends React.Component<NavBarProps> {
	render() {
		const { icon, iconText, onIconClick, children } = this.props;

		const iconCls = `text-center d-inline-block ml-2 mt-1${onIconClick ? " clickable" : ""}`;

		return (
			<nav className="navbar text-white bg-primary p-0 flex-shrink-0">
				<div className="w-25">
					<div className={iconCls} onClick={onIconClick}>
						{icon && <Icon icon={icon} text={iconText} />}
					</div>
				</div>
				<div className="w-50 text-center">{children}</div>
				<div className="w-25 d-flex justify-content-end">
					<img
						style={{ maxHeight: 48 }}
						src="images/CommuniCity-logo-blue.png"
					/>
				</div>
			</nav>
		);
	}
}
