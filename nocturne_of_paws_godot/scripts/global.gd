## Global.gd — Autoloaded singleton for game-wide state, save/load, and metrics.
extends Node

# ── Palette constants ─────────────────────────────────────────────────────────
const COLOR_OBSIDIAN     := Color(0.039, 0.031, 0.055)
const COLOR_DARK_MAROON  := Color(0.165, 0.024, 0.047)
const COLOR_DEEP_CRIMSON := Color(0.353, 0.039, 0.078)
const COLOR_CANDLE_GOLD  := Color(0.863, 0.627, 0.157)
const COLOR_GHOST_WHITE  := Color(0.902, 0.882, 0.922)

# ── Emotional metrics ─────────────────────────────────────────────────────────
var oxytocin_level: float = 0.0        ## Bond meter 0–100
var trust_level: float    = 0.0        ## Unlocks deep dialogue
var dread_level: float    = 0.0        ## Antagonist presence tracker

# ── Game progression ──────────────────────────────────────────────────────────
var current_act: int    = 1
var chapter: int        = 1
var flags: Dictionary   = {}          ## Story flags (quest/dialogue triggers)

# ── Save file path (mobile local storage) ─────────────────────────────────────
const SAVE_PATH := "user://nocturne_save.cfg"

# ── Signals ───────────────────────────────────────────────────────────────────
signal oxytocin_changed(new_value: float)
signal act_changed(new_act: int)
signal flag_set(flag_name: String)

# ─────────────────────────────────────────────────────────────────────────────

func _ready() -> void:
	load_game()

# ── Oxytocin API ──────────────────────────────────────────────────────────────

func add_oxytocin(amount: float) -> void:
	oxytocin_level = clampf(oxytocin_level + amount, 0.0, 100.0)
	emit_signal("oxytocin_changed", oxytocin_level)

func reduce_oxytocin(amount: float) -> void:
	add_oxytocin(-amount)

# ── Flag API ──────────────────────────────────────────────────────────────────

func set_flag(flag: String, value: Variant = true) -> void:
	flags[flag] = value
	emit_signal("flag_set", flag)

func has_flag(flag: String) -> bool:
	return flags.get(flag, false) as bool

# ── Save / Load (mobile ConfigFile) ──────────────────────────────────────────

func save_game() -> void:
	var cfg := ConfigFile.new()
	cfg.set_value("progress", "act",         current_act)
	cfg.set_value("progress", "chapter",     chapter)
	cfg.set_value("metrics",  "oxytocin",    oxytocin_level)
	cfg.set_value("metrics",  "trust",       trust_level)
	cfg.set_value("metrics",  "dread",       dread_level)
	cfg.set_value("flags",    "data",        var_to_str(flags))
	cfg.save(SAVE_PATH)

func load_game() -> void:
	var cfg := ConfigFile.new()
	if cfg.load(SAVE_PATH) != OK:
		return
	current_act    = cfg.get_value("progress", "act",      1)
	chapter        = cfg.get_value("progress", "chapter",  1)
	oxytocin_level = cfg.get_value("metrics",  "oxytocin", 0.0)
	trust_level    = cfg.get_value("metrics",  "trust",    0.0)
	dread_level    = cfg.get_value("metrics",  "dread",    0.0)
	var flag_str   = cfg.get_value("flags",    "data",     "{}")
	flags          = str_to_var(flag_str) if flag_str else {}

func delete_save() -> void:
	DirAccess.remove_absolute(SAVE_PATH)
	flags          = {}
	oxytocin_level = 0.0
	trust_level    = 0.0
	dread_level    = 0.0
	current_act    = 1
	chapter        = 1
