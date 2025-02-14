import json

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


	def get_title(self, wmclass=None, title=None):
		if wmclass is None and title is None:
			return None
		for t in self.window_rules:
			# from wmclass to wmclass
			if t["from_wmclass"] == wmclass and t["to_wmclass"] not in ["", None] and wmclass != None and t["rule"] == "global-title":
				return t["to_wmclass"]
			# from title to title
			if t["from_title"] == title and t["to_title"] not in ["", None] and title != None and t["rule"] == "global-title":
				return t["to_title"]
			# from wmclass to title
			if t["from_wmclass"] == wmclass and t["to_title"] not in ["", None] and wmclass != None and t["rule"] == "global-title":
				return t["to_title"]
			# from title to wmclass
			if t["from_title"] == title and t["to_wmclass"] not in ["", None] and title != None and t["rule"] == "global-title":
				return t["to_wmclass"]
		if wmclass is not None:
			return wmclass
		return title

	def get_translation(self, wmclass=None) -> (str):
		for t in self.translations:
			# from wmclass to wmclass
			if t["from_wmclass"] == wmclass:
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
