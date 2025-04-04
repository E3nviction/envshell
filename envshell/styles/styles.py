from styledwidgets.styled import styler, style_dict, on_hover
from styledwidgets.agents import colors, borderradius, transitions, margins, paddings
from styledwidgets.types import rem, px

button_style = style_dict(
	background_color=colors.gray.five,
	border_radius=rem(.75),
	padding=rem(.5),
	transition=transitions.fastest,
)

button_style_hover = button_style.copy()
button_style_hover.update(style_dict(
	background_color=colors.blue,
))