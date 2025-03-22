import json
import re

"""
Rules:
1. autohide-panel — Makes the panel be able to autohide when the app is in focus
2. global-title — Makes the App use its given Title when displayed
3. ignore — Ignore the workspace or app
"""

class Config:
	def __init__(self):
		self._config = {}
		self._config["window_rules"] = []
		self._config["translations"] = []
		self._config["workspace_rules"] = []
		self._config["shell_rules"] = []
		self._config["dock_pinned"] = {}
		self._private_config = None

	def window_rule(
		self,
		from_wmclass=None,
		from_title=None,
		to_wmclass=None,
		to_title=None,
		is_wmclass=None,
		is_title=None,
		rule="global-title"
	):
		"""Rule for Windows"""
		self._config["window_rules"].append({"from_wmclass": is_wmclass or from_wmclass, "from_title": is_title or from_title, "to_wmclass": to_wmclass, "to_title": to_title, "rule": rule})
	def workspace_rule(
		self,
		is_id=None,
		is_title=None,
		rule="ignore"
	):
		self._config["workspace_rules"].append({"is_id": is_id, "is_title": is_title, "rule": rule})
	def window_rename(
		self,
		from_wmclass=None,
		to_wmclass=None,
		is_wmclass=None,
	):
		self._config["translations"].append({"from_wmclass": is_wmclass or from_wmclass, "to_wmclass": to_wmclass})
	def shell_rule(
			self,
			rule="panel-position",
			value="top",
	):
		self._config["shell_rules"].append({"rule": rule, "value": value})

	@property
	def window_rules(self):
		return self._config["window_rules"]
	@property
	def translations(self):
		return self._config["translations"]
	@property
	def workspace_rules(self):
		return self._config["workspace_rules"]
	@property
	def shell_rules(self):
		return self._config["shell_rules"]
	@property
	def dock_pinned(self):
		return self._config["dock_pinned"]

	def pin_window(self, wmclass=None, command=None):
		self._config["dock_pinned"][wmclass] = command


	def get_title(self, wmclass=""):
		if wmclass in ["", None]:
			wmclass = ""
		for t in self.window_rules:
			is_correct_rule = t["rule"] == "global-title"
			is_wmclass = wmclass not in  ["", None]
			is_title_rule = t["to_title"] not in ["", None]
			wmclass_rule = "" if t["from_wmclass"] is None else t["from_wmclass"]
			if wmclass_rule == "": continue
			if re.match(wmclass_rule, wmclass) and is_wmclass and is_correct_rule:
				return t["to_title"]
		return wmclass

	def has_title(self, wmclass=None):
		if wmclass in ["", None]:
			return False
		for t in self.window_rules:
			is_correct_rule = t["rule"] == "global-title"
			is_title_rule = t["to_title"] not in ["", None]
			is_wmclass = wmclass not in  ["", None]
			wmclass_rule = "" if t["from_wmclass"] is None else t["from_wmclass"]
			if re.match(wmclass_rule, wmclass) and is_title_rule and is_wmclass and is_correct_rule:
				return True
		return False

	def get_translation(self, wmclass=None) -> (str):
		if wmclass in ["", None]:
			return wmclass
		for t in self.translations:
			wmclass_rule = "" if t["from_wmclass"] is None else t["from_wmclass"]
			# from wmclass to wmclass
			if re.match(wmclass_rule, wmclass):
				return t["to_wmclass"]
		return wmclass

	def is_window_ignored(self, wmclass=None, title=None):
		if wmclass is None and title is None:
			return False
		for t in self.window_rules:
			if t["from_wmclass"] == wmclass and wmclass not in ["", None] and t["rule"] == "ignore":
				return True
			if t["from_title"] == title and title not in ["", None] and t["rule"] == "ignore":
				return True
		return False

	def is_window_autohide(self, wmclass=None, title=None):
		if wmclass is None and title is None:
			return False
		for t in self.window_rules:
			if t["from_wmclass"] == wmclass and wmclass not in ["", None] and t["rule"] == "autohide-panel":
				return True
			if t["from_title"] == title and title not in ["", None] and t["rule"] == "autohide-panel":
				return True
		return False

	def is_workspace_ignored(self, id_=None, title=None):
		if id_ is None and title is None:
			return False
		for t in self.workspace_rules:
			if t["is_id"] == id_ and title is None and t["rule"] == "ignore":
				return True
			if t["is_title"] == title and id_ is None and t["rule"] == "ignore":
				return True
		return False

	def get_shell_rule(self, rule=None):
		for t in self.shell_rules:
			if t["rule"] == rule:
				return t["value"]
		return None

	def _get_recursive(self, rule_points: list, pre=None):
		if pre is None:
			pre = self._private_config
		if len(rule_points) == 0:
			return pre
		if rule_points[0] not in pre:
			return None
		return self._get_recursive(rule_points[1:], pre[rule_points[0]])

	def _set_recursive(self, rule_points: list, value, pre=None) -> dict:
		if pre is None:
			pre = self._private_config
		if len(rule_points) == 1:
			pre[rule_points[0]] = value
			return pre
		else:
			if rule_points[0] not in pre:
				pre[rule_points[0]] = {}
			pre[rule_points[0]] = self._set_recursive(rule_points[1:], value, pre[rule_points[0]])
			return pre

	def get_rule(self, rule_path=None, default=None, _type=None):
		rule_path = rule_path.split(".")
		val = self._get_recursive(rule_path) or default
		if _type == "tuple":
			fin_val = tuple(val)
			return fin_val
		return val

	def set_rule(self, rule_path=None, value=None):
		rule_path = rule_path.split(".")
		self._private_config = self._set_recursive(rule_path, value)