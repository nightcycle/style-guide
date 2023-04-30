from src.config import get_pseudo_enum_module_roblox_path, HEADER_WARNING, get_config, TypographyConfig, TextOverflow, CSS_TO_ROBLOX_FONT_WEIGHT, CSS_TO_ROBLOX_FONT_STYLE
from luau import indent_block
from luau.roblox.rojo import get_roblox_path_from_env_path
from luau.roblox import write_script, get_package_require
from luau.roblox.util import get_module_require
from luau.convert import from_any
from typing import Any
import os
import sys

def get_package_zip_path() -> str:
	base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
	print(base_path)
	for sub_path in os.listdir(base_path):
		print(sub_path)

	return os.path.join(base_path, "data\\Packages.zip")


def main(build_path: str, is_dark_mode=False):

	style_config = get_config()
	space_config = style_config["spacing"]

	pseudo_enum_ro_path = get_pseudo_enum_module_roblox_path()

	min_text_size = 100000000

	typography_configs: dict[str, TypographyConfig] = {}
	for k, possible_v in style_config.items():
		untyped_v: Any = possible_v
		if "font_size" in untyped_v:
			v: TypographyConfig = untyped_v
			typography_configs[k] = v
			min_text_size = min(v["font_size"], min_text_size)
	
	typography_scales = {}
	for k, v in typography_configs.items():
		typography_scales[k] = v["font_size"]/min_text_size

	border_width_scale = space_config["border_width"]/min_text_size
	padding_scale = space_config["padding"]/min_text_size
	border_radius_scale = space_config["border_radius"]/min_text_size

	contents = [
		"--strict",
		HEADER_WARNING,
		"",
		" -- Services",
		"local RunService = game:GetService(\"RunService\")",
		"",
		" -- Packages",
		"local Maid = " + get_package_require("Maid"),
		"local ColdFusion = " + get_package_require("ColdFusion"),
		"local CurveUtil = " + get_package_require("CurveUtil"),
		"local ServiceProxy = " + get_package_require("ServiceProxy"),
		"",
		" -- Modules",
		"local PseudoEnum = " + get_module_require(pseudo_enum_ro_path),
		"",
		" -- Types",
		"export type ContrastStandardType = PseudoEnum.ContrastStandardType",
		"export type GuiAlignmentType = PseudoEnum.GuiAlignmentType",
		"export type GuiCategoryType = PseudoEnum.GuiCategoryType",
		"export type GuiColorPalette = PseudoEnum.GuiColorPalette",
		"export type GuiDensityModifier = PseudoEnum.GuiDensityModifier",
		"export type GuiThemeType = PseudoEnum.GuiThemeType",
		"export type GuiTypography = PseudoEnum.GuiTypography",
		"",
		"type State<T> = ColdFusion.State<T>",
		"type ValueState<T> = ColdFusion.ValueState<T>",
		"type CanBeState<T> = (State<T> | T)",
		"type Maid = Maid.Maid",

		"-- Constants",
		# "local MIN_TEXT_SCALE = 0.2",
		f"local ABS_MIN_TEXT_SIZE = {min_text_size}",
		"local LUM_LIMIT = 0.03928",
		"local LUM_DENOM = 12.92",
		"local LUM_OFFSET = 0.055",
		"local LUM_OFFSET_DENOM = 1.055",
		"local R_WEIGHT = 0.2126",
		"local G_WEIGHT = 0.7152",
		"local B_WEIGHT = 0.0722",
		"local L_EXP = 2.4",
		"local MIN_HEX_DIFFERENCE = 100 / 255",
		"local BLACK_COLOR = Color3.fromHex(\"#000\")",
		"local WHITE_COLOR = Color3.fromHex(\"#FFF\")",
		"",
		f"local GAIN_COLOR = Color3.fromHex(\"{style_config['gain']['background_color']}\")",
		f"local LOSS_COLOR = Color3.fromHex(\"{style_config['loss']['background_color']}\")",
		f"local WARN_COLOR = Color3.fromHex(\"{style_config['warn']['background_color']}\")",
		f"local ERROR_COLOR = Color3.fromHex(\"{style_config['error']['background_color']}\")",
		f"local PRIMARY_DEFAULT_COLOR = Color3.fromHex(\"{style_config['primary']['background_color']}\")",
		f"local SECONDARY_DEFAULT_COLOR = Color3.fromHex(\"{style_config['secondary']['background_color']}\")",
		f"local TERTIARY_DEFAULT_COLOR = Color3.fromHex(\"{style_config['tertiary']['background_color']}\")",
		f"local BACKGROUND_DEFAULT_COLOR = Color3.fromHex(\"{style_config['background']['background_color']}\")",
		"",
		"local VALUE_RANGE = 0.3",
		"local VALUE_BUFFER = 0.05",
		"local SATURATION_RANGE = 0.1",
		"local CONTRAST_STANDARD_RATIOS: {[ContrastStandardType]: number} = {",
		] + indent_block([
			"Default = 4.5,",
			"LargeText = 3,",
			"Incidental = 0,",
			"Logotype = 0,",
		]) + [
		"}",
		"",
		"local ELEVATION_DATA = {",
		] + indent_block([
			"0,",
			"1,",
			"3,",
			"5,",
			"7,",
			"12",
		]) + [
		"}",
		"",
		"local STYLE_VARIANT_COUNTS = {",
		] + indent_block([
			"Primary = #ELEVATION_DATA,",
			"Secondary = #ELEVATION_DATA,",
			"Tertiary = #ELEVATION_DATA,",
			"Surface = #ELEVATION_DATA,",
			"Warning = 1,",
			"Error = 1,",
			"Loss = #ELEVATION_DATA,",
			"Gain = #ELEVATION_DATA,",
			"Dark = #ELEVATION_DATA,",
			"Light = #ELEVATION_DATA,",
		]) + [
		"}",
		"",
		"-- modifiers",
		"",
		"type Typography = {",
		] + indent_block([
			"Font: Font,",
			"Scale: number,",
			"TextWrapped: boolean,",
		]) + [
		"}",
		"",
		"type Paddings = {",
		"\t[GuiDensityModifier]: number,",
		"}",
		"",
		"local Typography: { [GuiTypography]: Typography } = {",
	]
		
	for typo_name, typo_config in typography_configs.items():
		font_family = typo_config["font_family"]
		scale = typography_scales[typo_name]
		text_wrapped = True
		if typo_config["text_overflow"] == "clip":
			text_wrapped = False

		font_weight = CSS_TO_ROBLOX_FONT_WEIGHT[typo_config["font_weight"]]
		font_style = CSS_TO_ROBLOX_FONT_STYLE[typo_config["font_style"]]
		contents += indent_block([
			f"{typo_name.title()} = " + "{"
			] + indent_block([
				f"Font = Font.fromName(\"{font_family}\", Enum.FontWeight.{font_weight}, Enum.FontStyle.{font_style}),",
				f"Scale = {scale},",
				f"TextWrapped = {from_any(text_wrapped)},",
			]) + [
			"},"	
		])

	contents += [
		"}",
		"",
		"local Paddings: Paddings = {",
		] + indent_block([
			"Default = 1,",
			"High = 0.75,",
			"Low = 1.5,",
		]) + [
		"}",
		"",

		"export type StyleGuide = {",
		] + indent_block([
			"__index: StyleGuide,",
			"Maid: Maid,",
			"new: (config: { [string]: any }?) -> StyleGuide,",
			"init: (maid: Maid) -> nil,",
			"getReadableColor: (color: Color3, background: Color3, contrastStandard: ContrastStandardType?) -> Color3,",
			"checkContrast: (color: Color3, background: Color3, contrastStandard: ContrastStandardType) -> boolean,",
			"getContrastRatio: (color: Color3, background: Color3) -> number,",
			"IsDarkMode: ValueState<boolean>,",
			"Primary: ValueState<Color3>,",
			"Secondary: ValueState<Color3>,",
			"Tertiary: ValueState<Color3>,",
			"Background: ValueState<Color3>,",
			# "MinimumTextScale: ValueState<number>,",
			"MinimumTextSize: State<number>,",
			"",
			"CornerRadius: State<UDim>,",
			"BorderSizePixel: State<number>,",
			"ViewportSize: State<Vector2>,",
			"",
			"_MinimumPaddingSize: State<number>,",
			"_Typography: State<GuiTypography>,",
			"_Paddings: State<{ [GuiDensityModifier]: number }>,",
			"_Palette: State<{ [GuiColorPalette]: Color3 }>,",
			"_Colors: { [GuiColorPalette]: State<Color3> },",
			"_ContrastColors: { [GuiColorPalette]: State<Color3> },",
			"_FullContrastColors: { [GuiColorPalette]: { [GuiColorPalette]: State<Color3> } },",
			"_TextSizeStates: { [GuiThemeType]: State<number> },",
			"_TextWrapStates: { [GuiThemeType]: State<boolean> },",
			"_TextFontStates: { [GuiThemeType]: State<Font> },",
			"_PaddingStates: { [GuiDensityModifier]: State<UDim> },",
			"Destroy: (self: StyleGuide) -> nil,",
			"",
			"GetPadding: (StyleGuide, CanBeState<GuiDensityModifier>) -> State<UDim>,",
			"GetTextSize: (StyleGuide, CanBeState<GuiTypography>) -> State<number>,",
			"GetTextWrapped: (StyleGuide, CanBeState<GuiTypography>) -> State<boolean>,",
			"GetFont: (StyleGuide, CanBeState<GuiTypography>) -> State<Font>,",
			"GetColor: (StyleGuide, CanBeState<GuiColorPalette>) -> State<Color3>,",
			"GetContrastColor: (StyleGuide, CanBeState<GuiColorPalette>, CanBeState<GuiColorPalette>?) -> State<Color3>,",
			"[any]: nil,",
		]) + [
		"}",
		"local Guide: StyleGuide = {} :: any",
		"Guide.__index = Guide",
		"",
		"function Guide:Destroy()",
		] + indent_block([
			"self.Maid:Destroy()",
			"local t: any = self",
			"for k, v in pairs(t) do",
			"\tt[k] = nil",
			"end",
			"setmetatable(t, nil)",
			"return nil",
		]) + [
		"end",
		"",
		"local currentGuide: StyleGuide",
		"",
		"function Guide.new(): StyleGuide",
		] + indent_block([
			"local _maid = Maid.new()",
			"local _fuse = ColdFusion.fuse(_maid)",
			"local _import = _fuse.import",
			"local _new = _fuse.new",
			"",
			"local _Computed = _fuse.Computed",
			"local _Value = _fuse.Value",
			"",
			"local Primary = _Value(PRIMARY_DEFAULT_COLOR)",
			"local Secondary = _Value(SECONDARY_DEFAULT_COLOR)",
			"local Tertiary = _Value(TERTIARY_DEFAULT_COLOR)",
			"local Background = _Value(BACKGROUND_DEFAULT_COLOR)",
			"",
			"local ViewportSize = _Value(workspace.CurrentCamera.ViewportSize)",
			"_maid:GiveTask(RunService.RenderStepped:Connect(function()",
			"	ViewportSize:Set(workspace.CurrentCamera.ViewportSize)",
			"end))",
			"",
			"local Palette = _Computed(",
			] + indent_block([
				"function(",
				] + indent_block([
					"primary: Color3,",
					"secondary: Color3,",
					"tertiary: Color3,",
					"background: Color3",
				]) + [
				"): { [PseudoEnum.GuiColorPalette]: Color3 }",
				] + indent_block([
					"local palette = {}",
					"",
					"local function getBrightness(elevation: number)",
					"\tlocal maxElevation = ELEVATION_DATA[#ELEVATION_DATA]",
					"\treturn (elevation / maxElevation) ^ 0.5",
					"end",
					"",
					"for key: string, count in pairs(STYLE_VARIANT_COUNTS) do",
					] + indent_block([
						"for i = 1, count do",
						] + indent_block([
							"local enum: PseudoEnum.GuiColorPalette? = PseudoEnum.GuiColorPalette[(key .. if count == 1 then \"\" else tostring(i)) :: any]",
							"assert(enum)",
							"",
							"local h: number, s: number, v: number",
							"if key == \"Surface\" then",
							"\th, s, v = background:ToHSV()",
							"elseif key == \"Primary\" then",
							"\th, s, v = primary:ToHSV()",
							"elseif key == \"Secondary\" then",
							"\th, s, v = secondary:ToHSV()",
							"elseif key == \"Tertiary\" then",
							"\th, s, v = tertiary:ToHSV()",
							"elseif key == \"Warning\" then",
							"\th, s, v = WARN_COLOR:ToHSV()",
							"elseif key == \"Loss\" then",
							"\th, s, v = LOSS_COLOR:ToHSV()",
							"elseif key == \"Gain\" then",
							"\th, s, v = GAIN_COLOR:ToHSV()",
							"elseif key == \"Dark\" then",
							"\th, s, v = BLACK_COLOR:ToHSV()",
							"elseif key == \"Light\" then",
							"\th, s, v = WHITE_COLOR:ToHSV()",
							"else",
							"\th, s, v = ERROR_COLOR:ToHSV()",
							"end",
							"",
							"-- gets elevation level",
							"local top = {",
							"\tSaturation = math.max(0, s - SATURATION_RANGE),",
							"\tValue = math.min(1 - VALUE_BUFFER, v + VALUE_RANGE),",
							"}",
							"local bottom = {",
							"\tSaturation = math.min(1, top.Saturation + SATURATION_RANGE),",
							"\tValue = math.max(VALUE_BUFFER, top.Value - VALUE_RANGE),",
							"}",
							"top.Saturation = bottom.Saturation - SATURATION_RANGE",
							"top.Value = bottom.Value + VALUE_RANGE",
							"",
							"local brightness = getBrightness(ELEVATION_DATA[i])",
							"",
							"palette[enum] = Color3.fromHSV(",
							"\th,",
							"\tCurveUtil.lerp(bottom.Saturation, top.Saturation, brightness),",
							"\tCurveUtil.lerp(bottom.Value, top.Value, brightness)",
							")",
						]) + [
						"end",
					]) + [
					"end",
					"return palette",
				]) + [
				"end,",
				"Primary,",
				"Secondary,",
				"Tertiary,",
				"Background",
			]) + [
			")",
			# "local MinTextScale = _Value(MIN_TEXT_SCALE)",
			"local MinTextSize = _Computed(function(vSize: Vector2): number",
			"\treturn math.max(math.ceil(0.05 * vSize.Y), ABS_MIN_TEXT_SIZE)",
			"end, ViewportSize)",
			"local MinimumTextSizeTween = MinTextSize:Tween()",
			"",
			"local self: StyleGuide = setmetatable({",
			] + indent_block([
				"Primary = Primary,",
				"Secondary = Secondary,",
				"Tertiary = Tertiary,",
				f"IsDarkMode = _Value({from_any(is_dark_mode)}),",
				"Background = Background,",
				"Maid = _maid,",
				"_Paddings = _Value(Paddings),",
				"_Typography = _Value(Typography) :: State<{ [GuiThemeType]: Typography }>,",
				"_MinimumPaddingSize = _Computed(function(minTextSize: number): number",
				f"\treturn math.max(math.ceil(minTextSize * {padding_scale}), 1)",
				"end, MinimumTextSizeTween),",
				# "MinimumTextScale = MinTextScale,",
				"MinimumTextSize = MinTextSize,",
				"ViewportSize = ViewportSize,",
				"_Palette = Palette,",
				"CornerRadius = _Computed(function(minTextSize: number)",
				f"\tminTextSize = math.max(math.round(minTextSize * {border_radius_scale}), 1) :: number",
				"\treturn UDim.new(0, minTextSize)",
				"end, MinimumTextSizeTween),",
				"BorderSizePixel = _Computed(function(minTextSize: number)",
				f"\treturn math.max(math.round(minTextSize * {border_width_scale}), 1)",
				"end, MinimumTextSizeTween),",
				"_Colors = {} :: { [GuiColorPalette]: State<Color3>? },",
				"_ContrastColors = {} :: { [GuiColorPalette]: State<Color3>? },",
				"_FullContrastColors = {},",
				"_TextSizeStates = {} :: { [GuiThemeType]: State<number>? },",
				"_TextWrapStates = {} :: { [GuiThemeType]: State<boolean>? },",
				"_TextFontStates = {} :: { [GuiThemeType]: State<Font>? },",
				"_PaddingStates = {} :: { [GuiDensityModifier]: State<UDim>? },",
			]) + [
			"}, Guide) :: any",
			"",
			"for i, enumItem in ipairs(PseudoEnum.getEnumItems(\"GuiColorPalette\")) do",
			] + indent_block([
				"self._Colors[enumItem] = _Computed(function(palette)",
				] + indent_block([
					"if not palette then",
					"\treturn Color3.new(0, 0, 0)",
					"end",
					"return palette[enumItem] or Color3.new(0, 0, 0)",
				]) + [
				"end, Palette):Tween(0.5)",
			]) + [
			"end",
			"for i, enumItem in ipairs(PseudoEnum.getEnumItems(\"GuiColorPalette\")) do",
			] + indent_block([
				"self._ContrastColors[enumItem] = _Computed(function(background: Color3)",
				"\treturn Guide.getReadableColor(Color3.fromHSV(0, 0, 0.5), background)",
				"end, self._Colors[enumItem])",
				"self._FullContrastColors[enumItem] = {}",
				"for j, backEnumItem in ipairs(PseudoEnum.getEnumItems(\"GuiColorPalette\")) do",
				] + indent_block([
					"self._FullContrastColors[enumItem][backEnumItem] = _Computed(function(front: Color3, background: Color3)",
					"\treturn Guide.getReadableColor(front, background)",
					"end, self._Colors[enumItem], self._Colors[backEnumItem])",
				]) + [
				"end",
			]) + [
			"end",
			"",
			"_Computed(function(typography: PseudoEnum.GuiTypography, minTextSize: number)",
			] + indent_block([
				"for enumItem: PseudoEnum.GuiThemeType, data: Typography in pairs(typography) do",
				] + indent_block([
					"local TSS: any = self._TextSizeStates[enumItem] or _Value(nil)",
					"local TextStateSize: ValueState<number> = TSS",
					"TextStateSize:Set(math.ceil(data.Scale * minTextSize))",
					"self._TextSizeStates[enumItem] = TextStateSize",
					"",
					"local TWS: any = self._TextWrapStates[enumItem] or _Value(nil)",
					"local TextWrapState: ValueState<boolean> = TWS",
					"TextWrapState:Set(data.TextWrapped)",
					"self._TextWrapStates[enumItem] = TextWrapState",
					"",
					"local TFS: any = self._TextFontStates[enumItem] or _Value(nil)",
					"local TextFontState: ValueState<Font> = TFS",
					"TextFontState:Set(data.Font)",
					"self._TextFontStates[enumItem] = TextFontState",
				]) + [
				"end",
				"return nil",
			]) + [
			"end, self._Typography, MinimumTextSizeTween)",
			"",
			"_Computed(function(paddings: Paddings, minTextSize: number)",
			] + indent_block([
				"for enumItem, val: number in pairs(paddings) do",
				] + indent_block([
					"local PS: any = self._PaddingStates[enumItem] or _Value(nil)",
					"local PaddingState: ValueState<UDim> = PS",
					"PaddingState:Set(UDim.new(0, math.ceil(val * minTextSize)))",
					"self._PaddingStates[enumItem] = PaddingState",
				]) + [
				"end",
				"return nil",
			]) + [
			"end, self._Paddings, MinimumTextSizeTween)",
			"",
			"setmetatable(self, Guide)",
			"",
			"currentGuide = self :: any",
			"return self :: any",
		]) + [
		"end",
			"",
			"function handleDynamicEnum<T, G>(pseudo: CanBeState<T>, options: { [T]: State<G> }): State<G>",
			] + indent_block([
				"local state = pseudo :: any",
				"",
				"if state.Get == nil then",
				"\treturn options[state]",
				"else",
				] + indent_block([
					"return ColdFusion.Computed(function(key: T): G",
					] + indent_block([
						"local vals = {}",
						"for k, v: State<G> in pairs(options) do",
						"\tvals[k] = v:Get()",
						"end",
						"return vals[key]",
					]) + [
					"end, state)",
				]) + [
				"end",
			]) + [
			"end",
			"function handleDoubleDynamicEnum<T, G>(",
			] + indent_block([
				"pseudo1: CanBeState<T>,",
				"pseudo2: CanBeState<T>,",
				"options: { [T]: { [T]: State<G> } }",
			]) + [
			"): State<G>",
			] + indent_block([
				"local state1 = pseudo1 :: any",
				"local state2 = pseudo2 :: any",
				"if state1.EnumType ~= nil and state2.EnumType ~= nil then",
				"\treturn options[state1][state2]",
				"elseif state1.EnumType == nil and state2.EnumType == nil then",
				] + indent_block([
				"return ColdFusion.Computed(function(key1: T, key2: T): G",
				] + indent_block([
					"local vals = {}",
					"for k1, v1: { [T]: State<G> } in pairs(options) do",
					] + indent_block([
						"vals[k1] = {}",
						"for k2, v2: State<G> in pairs(v1) do",
						"\tvals[k1][k2] = v2:Get()",
						"end",
					]) + [
					"end",
					"return vals[key1][key2]",
				]) + [
				"end, state1, state2)",
				]) + [
				"elseif state1.EnumType == nil then",
				] + indent_block([
					"return ColdFusion.Computed(function(key1: T): G",
					] + indent_block([
						"local vals = {}",
						"for k1, v1: { [T]: State<G> } in pairs(options) do",
						] + indent_block([
							"vals[k1] = {}",
							"for k2, v2: State<G> in pairs(v1) do",
							"\tvals[k1][k2] = v2:Get()",
							"end",
						]) + [
						"end",
						"return vals[key1][state2]",
					]) + [
					"end, state1)",
				]) + [
				"elseif state2.EnumType == nil then",
				] + indent_block([
					"return ColdFusion.Computed(function(key2: T): G",
					] + indent_block([
						"local vals = {}",
						"for k1, v1: { [T]: State<G> } in pairs(options) do",
						] + indent_block([
							"vals[k1] = {}",
							"for k2, v2: State<G> in pairs(v1) do",
							"\tvals[k1][k2] = v2:Get()",
							"end",
						]) + [
						"end",
						"return vals[state1][key2]",
					]) + [
					"end, state2)",
					]) + [
				"end",
				"error(\"Bad params\")",
			]) + [
			"end",
			"",
			"function Guide:GetPadding(guiDensityModifier: CanBeState<PseudoEnum.GuiDensityModifier>): State<UDim>",
			"\tassert(guiDensityModifier ~= nil, \"Bad GuiDensityModifier\")",
			"\treturn handleDynamicEnum(guiDensityModifier, self._PaddingStates)",
			"end",
			"",
			"function Guide:GetTextSize(guiTypography: CanBeState<PseudoEnum.GuiTypography>): State<number>",
			"\tassert(guiTypography ~= nil, \"Bad GuiTypography\")",
			"\treturn handleDynamicEnum(guiTypography, self._TextSizeStates)",
			"end",
			"",
			"function Guide:GetTextWrapped(guiTypography: CanBeState<PseudoEnum.GuiTypography>): State<boolean>",
			"\tassert(guiTypography ~= nil, \"Bad GuiTypography\")",
			"\treturn handleDynamicEnum(guiTypography, self._TextWrapStates)",
			"end",
			"function Guide:GetFont(guiTypography: CanBeState<PseudoEnum.GuiTypography>): State<Font>",
			"\tassert(guiTypography ~= nil, \"Bad GuiTypography\")",
			"\treturn handleDynamicEnum(guiTypography, self._TextFontStates)",
			"end",
			"",
			"function Guide:GetColor(guiColorPalette: CanBeState<PseudoEnum.GuiColorPalette>): State<Color3>",
			"\tassert(guiColorPalette ~= nil, \"Bad GuiColorPalette\")",
			"\treturn handleDynamicEnum(guiColorPalette, self._Colors)",
			"end",
			"",
			"function Guide:GetContrastColor(",
			"\tbackColorPalette: CanBeState<PseudoEnum.GuiColorPalette>,",
			"\tgoalColorPalette: CanBeState<PseudoEnum.GuiColorPalette>?",
			"): State<Color3>",
			] + indent_block([
				"assert(backColorPalette ~= nil, \"Bad GuiColorPalette\")",
				"if goalColorPalette == nil then",
				"\treturn handleDynamicEnum(backColorPalette, self._ContrastColors)",
				"else",
				"\tassert(goalColorPalette ~= nil)",
				"\treturn handleDoubleDynamicEnum(goalColorPalette, backColorPalette, self._FullContrastColors)",
				"end",
			]) + [
			"end",
			"",
			"function Guide.getContrastRatio(foreground: Color3, background: Color3): number",
			] + indent_block([
				"local function getRelativeLuminance(color: Color3): number",
				] + indent_block([
					"local function solveSpace(v: number): number",
					] + indent_block([
						"if v < LUM_LIMIT then",
						"\treturn v / LUM_DENOM",
						"else",
						"\treturn ((v + LUM_OFFSET) / LUM_OFFSET_DENOM) ^ L_EXP",
						"end",
					]) + [
					"end",
					"return R_WEIGHT * solveSpace(color.R) + G_WEIGHT * solveSpace(color.G) + B_WEIGHT * solveSpace(color.B)",
				]) + [
				"end",
				"",
				"local _fH, _fS, fV = foreground:ToHSV()",
				"local _bH, _bS, bV = background:ToHSV()",
				"",
				"local fLum = getRelativeLuminance(foreground)",
				"local bLum = getRelativeLuminance(background)",
				"",
				"local lighterRelativeLuminance: number",
				"local darkerRelativeLuminance: number",
				"if fV < bV then",
				"\tlighterRelativeLuminance = bLum",
				"\tdarkerRelativeLuminance = fLum",
				"else",
				"\tlighterRelativeLuminance = fLum",
				"\tdarkerRelativeLuminance = bLum",
				"end",
				"",
				"return (lighterRelativeLuminance + 0.05) / (darkerRelativeLuminance + 0.05)",
			]) + [
			"end",
			"",
			"function Guide.checkContrast(",
			"\tcolor: Color3,",
			"\tbackground: Color3,",
			"\tcontrastStandard: PseudoEnum.ContrastStandardType",
			"): boolean",
			"\tlocal minRatio = CONTRAST_STANDARD_RATIOS[contrastStandard]",
			"\tlocal ratio = Guide.getContrastRatio(color, background)",
			"\treturn ratio >= minRatio",
			"end",
			"",
			"-- https://github.com/alex-page/a11ycolor/blob/main/index.js",
			"function Guide.getReadableColor(",
			"\tcolor: Color3,",
			"\tbackground: Color3,",
			"\tcontrastStandard: PseudoEnum.ContrastStandardType?",
			"): Color3",
			] + indent_block([
				"contrastStandard = PseudoEnum.ContrastStandardType.Default",
				"assert(contrastStandard ~= nil)",
				"",
				"-- Check the ratio straight away, if it passes return the value as hex",
				"if Guide.checkContrast(color, background, contrastStandard) then",
				"\treturn color",
				"end",
				"",
				"-- Ratio didn't pass so we need to find the nearest color",
				"local isBlackContrast = Guide.checkContrast(BLACK_COLOR, background, contrastStandard)",
				"local isWhiteContrast = Guide.checkContrast(WHITE_COLOR, background, contrastStandard)",
				"",
				"local cH, cS, cV = color:ToHSV()",
				"local minValue = 0",
				"local maxValue = 1",
				"local isDarkColor = false",
				"",
				"-- If black and white both pass on the background",
				"if isBlackContrast and isWhiteContrast then",
				] + indent_block([
					"-- Change the min lightness if the color is light",
					"if cV >= 0.5 then",
					"\tminValue = cV",
					"else -- Change the max lightness if the color is dark",
					"\tmaxValue = cV",
					"\tisDarkColor = true",
					"end",
				]) + [
				"elseif isBlackContrast then -- If our colour passes contrast on black",
				"\tmaxValue = cV",
				"\tisDarkColor = true",
				"else -- Colour doesn't meet contrast pass on black",
				"\tminValue = cV",
				"end",
				"",
				"-- The color to return",
				"local finalColor: Color3?",
				"",
				"-- Binary search until we find the colour that meets contrast",
				"local prevColor: Color3?",
				"while not finalColor do",
				] + indent_block([
					"local midValue = (minValue + maxValue) / 2",
					"local midColor = Color3.fromHSV(cH, cS, midValue)",
					"if Guide.checkContrast(midColor, background, contrastStandard) then",
					] + indent_block([
						"if maxValue - minValue <= MIN_HEX_DIFFERENCE then",
						"\tfinalColor = midColor",
						"elseif isDarkColor then",
						"\tminValue = midValue",
						"else",
						"\tmaxValue = midValue",
						"end",
					]) + [
					"elseif isDarkColor then",
					"\tmaxValue = midValue",
					"else",
					"\tminValue = midValue",
					"end",
					"if prevColor == midColor then",
					"\tbreak",
					"end",
					"prevColor = midColor",
				]) + [
				"end",
				"return finalColor or color",
			]) + [
			"end",
			"",
			"local proxy = ServiceProxy(function()",
			"\treturn currentGuide or Guide",
			"end)",
			"",
			"function Guide.init(maid: Maid)",
			"\tmaid:GiveTask(Guide.new())",
			"\treturn nil",
			"end",
		"",
		"return proxy"
	]

	write_script(build_path, "\n".join(contents), packages_dir_zip_file_path=get_package_zip_path())