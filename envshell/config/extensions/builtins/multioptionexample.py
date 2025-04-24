import sys

if len(sys.argv) == 1:
    print("""[
	{
		"name": "Multi Options!!! Yay",
		"tooltip": "We finally have Multiple Options",
		"desc": "Oh yeah!",
		"on-click": "notify-send Yay Multi-Options"
	},
    {
		"name": "Open Home Folder",
		"tooltip": "~ directory",
		"desc": "Mi Hermano es un Gato!",
		"on-click": "xdg-open ~"
	}
]""")
else:
    if sys.argv[1].startswith("multi-options"):
        print("true")
