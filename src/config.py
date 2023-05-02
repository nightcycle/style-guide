import os
import toml
import tinycss2
import dpath
from luau.roblox.rojo import get_roblox_path_from_env_path
from typing import TypedDict, Any, Literal

FOREMAN_PSEUDO_ENUM_PATH = "nightcycle/pseudo-enum"
FOREMAN_PSEUDO_ENUM_VERSION = "0.1.0"

HEADER_WARNING = "-- this script was generated by nightcycle/style-guide, do not manually edit"

CONFIG_PATH = "style.css"

FontWeight = Literal["bold", "normal", "lighter", "bolder", "100", "200", "300", "400", "500", "600", "700", "800", "900"]
Alignment = Literal["center", "left", "right", "top", "bottom", "top-left", "top-right", "bottom-left", "bottom-right"]
TextOverflow = Literal["clip", "wrap"]
FontStyle = Literal["normal", "italic"]
FontFamily = Literal[
	"Accanthis ADF Std",
	"Amatic SC",
	"Arial",
	"Arial (Legacy)",
	"Balthazar",
	"Bangers",
	"Comic Neue Angular	",
	"Creepster",
	"Denk One",
	"Fondamento",
	"Fredoka One",
	"Gotham SSm",
	"Grenze Gotisch",
	"Guru",
	"Highway Gothic",
	"Inconsolata",
	"Indie Flower",
	"Josefin Sans",
	"Jura",
	"Kalam",
	"Luckiest Guy",
	"Merriweather",
	"Michroma",
	"Nunito",
	"Oswald",
	"Patrick Hand",
	"Permanent Marker",
	"Press Start 2P",
	"Roboto",
	"Roboto Condensed",
	"Roboto Mono",
	"Roman Antique",
	"Sarpanch",
	"Source Sans Pro",
	"Special Elite	",
	"Titillium Web",
	"Ubuntu",
	"Zekton",
]
RobloxFontWeight = Literal["Thin", "ExtraLight", "Light", "Regular", "Medium", "SemiBold", "Bold", "ExtraBold", "Heavy"]
RobloxFontStyle = Literal["Italic", "Normal"]

CSS_TO_ROBLOX_FONT_WEIGHT = {
	"bold": "Bold", 
	"normal": "Regular", 
	"lighter": "ExtraLight", 
	"bolder": "ExtraBold", 
	"100": "Thin", 
	"200": "ExtraLight", 
	"300": "Light", 
	"400": "Regular", 
	"500": "Medium",  
	"600": "SemiBold", 
	"700": "Bold",  
	"800": "ExtraBold",  
	"900": "Heavy",
}

CSS_TO_ROBLOX_FONT_STYLE = {
	"normal": "Normal", 
	"italic": "Italic", 
}

class TypographyConfig(TypedDict):
	font_family: FontFamily
	font_size: int
	font_weight: FontWeight
	font_style: FontStyle
	text_overflow: TextOverflow

class SpacingConfig(TypedDict):
	border_width: int
	padding: int
	border_radius: int

class ColorConfig(TypedDict): 
	background_color: str

class StyleConfig(TypedDict):
	headline1: TypographyConfig
	headline2: TypographyConfig
	headline3: TypographyConfig
	headline4: TypographyConfig
	headline5: TypographyConfig
	headline6: TypographyConfig
	subtitle1: TypographyConfig
	subtitle2: TypographyConfig
	body1: TypographyConfig
	body2: TypographyConfig
	button: TypographyConfig
	caption: TypographyConfig
	overline: TypographyConfig
	spacing: SpacingConfig
	primary: ColorConfig
	secondary: ColorConfig
	tertiary: ColorConfig
	background: ColorConfig
	error: ColorConfig
	warn: ColorConfig
	gain: ColorConfig	
	loss: ColorConfig	

def hsv_to_rgb(h: float, s: float, v: float) -> tuple[int, int, int]:
	int_v: int = int(v)

	if s == 0.0:
		return int_v, int_v, int_v
	i = int(h*6.) # XXX assume int() truncates!
	f = (h*6.)-i
	p: int = int(v*(1.-s)) 
	q: int = int(v*(1.-s*f))
	t: int = int(v*(1.-s*(1.-f)))
	
	i %= 6
	if i == 0:
		return int_v, t, p
	if i == 1:
		return q, int_v, p
	if i == 2:
		return p, int_v, t
	if i == 3:
		return p, q, int_v
	if i == 4:
		return t, p, int_v
	if i == 5:
		return int_v, p, q

	raise ValueError(f"bad h,s,v: {h}, {s}, {v}")


def rgb_to_hex(r:int, g:int, b:int):
    """Convert RGB to HEX."""
    return '#{:02x}{:02x}{:02x}'.format(r, g, b)


def css_to_json(css_file) -> dict | list:
    # Read the contents of the CSS file
    with open(css_file, 'r') as file:
        css_text = file.read()
    
    # Parse the CSS
    parsed_css = tinycss2.parse_stylesheet(css_text, skip_comments=True, skip_whitespace=True)
    
    # Extract the rules and convert them to JSON
    css_json = {}
    for rule in parsed_css:
        if rule.type == 'qualified-rule':
            selector = tinycss2.serialize(rule.prelude)
            declarations = tinycss2.parse_declaration_list(rule.content)
            properties = {}
            for declaration in declarations:
                if declaration.type == 'declaration':
                    property_name = declaration.lower_name
                    property_value = tinycss2.serialize(declaration.value).strip()
                    properties[property_name] = property_value
            css_json[selector] = properties
    
    return css_json

def parse_css_color_str_to_hex(text: str) -> str:
	text = text.replace("(", "").replace(")", "")
	if text[0:3] == "rgb":
		text = text[3:]
		values = text.split(",")
		r = int(values[0])
		g = int(values[1])
		b = int(values[2])
		return rgb_to_hex(r,g,b)
	elif text[0:4] == "hsla":
		text = text[4:]
		values = text.split(",")
		h = float(values[0])
		s = float(values[1])
		v = float(values[2])
		r,g,b = hsv_to_rgb(h,s,v)
		return rgb_to_hex(int(r*255),int(g*255),int(b*255))
	elif text[0] == "#":
		return text

	raise ValueError(f"bad prefix: {text}")

DEFAULT_STYLE_CSS = """
.headline1 {
	font-family: 'Arial';
	font-size: 48px;
	font-style: normal;
	font-weight: bold;
	text-overflow: wrap;
}

.headline2 {
	font-family: 'Arial';
	font-size: 32px;
	font-style: normal;
	font-weight: bold;
	text-overflow: wrap;
}

.headline3 {
	font-family: 'Arial';
	font-size: 28px;
	font-style: normal;
	font-weight: bold;
	text-overflow: clip;
}

.headline4 {
	font-family: 'Arial';
	font-size: 24px;
	font-style: normal;
	font-weight: bold;
	text-overflow: clip;
}

.headline5 {
	font-family: 'Arial';
	font-size: 22px;
	font-style: normal;
	font-weight: bold;
	text-overflow: clip;
}

.headline6 {
	font-family: 'Arial';
	font-size: 20px;
	font-style: normal;
	font-weight: bold;
	text-overflow: clip;
}

.subtitle1 {
	font-family: 'Arial';
	font-size: 18px;
	font-style: normal;
	font-weight: bold;
	text-overflow: clip;
}

.subtitle2 {
	font-family: 'Arial';
	font-size: 16px;
	font-style: normal;
	font-weight: bold;
	text-overflow: clip;
}

.button {
	font-family: 'Arial';
	font-size: 15px;
	font-style: normal;
	font-weight: bold;
	text-overflow: clip;
}

.body1 {
	font-family: 'Arial';
	font-size: 12px;
	font-style: normal;
	font-weight: bold;
	text-overflow: clip;
}

.body2 {
	font-family: 'Arial';
	font-size: 11px;
	font-style: normal;
	font-weight: bold;
	text-overflow: clip;
}

.caption {
	font-family: 'Ubuntu';
	font-size: 9px;
	font-style: normal;
	font-weight: bold;
	text-overflow: clip;
}

.overline {
	font-family: 'Ubuntu';
	font-size: 8px;
	font-style: normal;
	font-weight: bold;
	text-overflow: clip;
}

.spacing {
	border-width: 2px;
	padding: 6px;
	border-radius: 4px;
}

.primary {
	background-color: rgb(0, 136, 255);
}

.secondary {
	background-color: rgb(255, 187, 0);
}

.tertiary {
	background-color:rgb(104, 255, 235);
}

.background {
	background-color: hsla(0.5, 0, 0.1, 1);
}

.error {
	background-color: #ff0000;
}

.warn {
	background-color: #ffbf00;
}

.gain {
	background-color: #33cc33;
}

.loss {
	background-color: #ff0000;
}
"""

ENUM_REGISTRY = {
	"ContrastStandardType": [ 
		"Default", 
		"LargeText", 
		"Incidental", 
		"Logotype" 
	],
	"GuiAlignmentType": [
		"Center",
		"Left",
		"Right",
		"Top",
		"Bottom",
		"TopLeft",
		"TopRight",
		"BottomLeft",
		"BottomRight"
	],
	"GuiCategoryType": [
		"Background",
		"Panel",
		"Card",
		"Frame",
		"Item",
		"Button",
		"Label",
		"Bar",
		"Toggle"
	],
	"GuiColorPalette": [
		"Primary1",
		"Primary2",
		"Primary3",
		"Primary4",
		"Primary5",
		"Primary6",
		"Secondary1",
		"Secondary2",
		"Secondary3",
		"Secondary4",
		"Secondary5",
		"Secondary6",
		"Tertiary1",
		"Tertiary2",
		"Tertiary3",
		"Tertiary4",
		"Tertiary5",
		"Tertiary6",
		"Surface1",
		"Surface2",
		"Surface3",
		"Surface4",
		"Surface5",
		"Surface6",
		"Warning",
		"Error",
		"Loss1",
		"Loss2",
		"Loss3",
		"Loss4",
		"Loss5",
		"Loss6",
		"Gain1",
		"Gain2",
		"Gain3",
		"Gain4",
		"Gain5",
		"Gain6",
		"Dark1",
		"Dark2",
		"Dark3",
		"Dark4",
		"Dark5",
		"Dark6",
		"Light1",
		"Light2",
		"Light3",
		"Light4",
		"Light5",
		"Light6"
	],
	"GuiDensityModifier": [
		"Default", 
		"High", 
		"Low" 
	],
	"GuiThemeType": [ 
		"Dark", 
		"Light"
	],
	"GuiTypography": [
		"Overline",
		"Caption",
		"Body2",
		"Body1",
		"Subtitle2",
		"Subtitle1",
		"Button",
		"Headline6",
		"Headline5",
		"Headline4",
		"Headline3",
		"Headline2",
		"Headline1"
	],
}

def get_config() -> StyleConfig:
	init_config: Any = {}
	untyped_css_json: Any = css_to_json(CONFIG_PATH)
	css_json: dict = untyped_css_json
	for path, val in dpath.search(css_json, '**', yielded=True):
		if type(val) != dict and type(val) != list:
			formatted_path = path.replace(".", "").replace("-", "_").replace(" ", "")
			formatted_value = val.replace("\"", "")
			dpath.new(init_config, formatted_path, formatted_value)

	for class_name, class_value in init_config.items():
		if "background_color" in class_value:
			class_value["background_color"] = parse_css_color_str_to_hex(class_value["background_color"])
		for k, v in class_value.items():
			suffix = v[(len(v)-2):(len(v))]
			if suffix == "px":
				v = v.replace("px", "")
				class_value[k] = int(v)

	return init_config

def get_pseudo_enum_module_roblox_path(rojo_project_path="default.project.json") -> str:
	if os.path.exists("pseudo-enum.toml"):

		with open("pseudo-enum.toml", "r") as pseudo_file:
			pseudo_config = toml.loads(pseudo_file.read())

		build_path = pseudo_config["build_path"]
		enum_config = pseudo_config["enums"]
		for k, v in ENUM_REGISTRY.items():
			if k in enum_config and len(enum_config[k]) != len(v):
				raise ValueError(f"different type already defined for {k}")

			enum_config[k] = v

		with open("pseudo-enum.toml", "w") as write_file:
			write_file.write(toml.dumps(pseudo_config))

		return get_roblox_path_from_env_path(build_path, rojo_project_path)
	
	raise ValueError("nightcycle/pseudo-enum is required for this tool.")

def init_config():
	assert not os.path.exists(CONFIG_PATH), "style.css already exists"
	config_file = open(CONFIG_PATH, "w")
	config_file.write(DEFAULT_STYLE_CSS)
	config_file.close()