## StateManager.gd — Autoloaded scene-stack state machine with transition support.
extends Node

# ── Signals ───────────────────────────────────────────────────────────────────
signal state_changed(new_state: String)
signal transition_started(type: String)
signal transition_finished

# ── Scene registry ───────────────────────────────────────────────────────────
const SCENES := {
	"main_menu":    "res://scenes/main_menu.tscn",
	"act1_citadel": "res://scenes/act1_citadel.tscn",
	"act2_swamp":   "res://scenes/act2_swamp.tscn",
	"waltz_game":   "res://scenes/waltz_game.tscn",
}

var _stack: Array[String]  = []
var _current_scene: Node   = null
var _transitioning: bool   = false

@onready var _transition_layer: CanvasLayer = $TransitionLayer
@onready var _fade_rect: ColorRect          = $TransitionLayer/FadeRect

func _ready() -> void:
	_fade_rect.color = Color(0, 0, 0, 1)

# ── Public API ────────────────────────────────────────────────────────────────

func goto(state_name: String, transition: String = "fade") -> void:
	if _transitioning:
		return
	_transitioning = true
	emit_signal("transition_started", transition)
	await _fade_out(0.35)
	_load_scene(state_name)
	_stack.clear()
	_stack.append(state_name)
	await _fade_in(0.35)
	_transitioning = false
	emit_signal("state_changed", state_name)
	emit_signal("transition_finished")

func push(state_name: String) -> void:
	if _transitioning:
		return
	_stack.append(state_name)
	_transitioning = true
	await _fade_out(0.2)
	_load_scene(state_name)
	await _fade_in(0.2)
	_transitioning = false
	emit_signal("state_changed", state_name)

func pop() -> void:
	if _transitioning or _stack.size() <= 1:
		return
	_stack.pop_back()
	var prev := _stack[-1]
	_transitioning = true
	await _fade_out(0.2)
	_load_scene(prev)
	await _fade_in(0.2)
	_transitioning = false
	emit_signal("state_changed", prev)

func current_state() -> String:
	return _stack[-1] if _stack.size() > 0 else ""

# ── Internals ─────────────────────────────────────────────────────────────────

func _load_scene(state_name: String) -> void:
	if not SCENES.has(state_name):
		push_error("StateManager: unknown state '%s'" % state_name)
		return
	if _current_scene:
		_current_scene.queue_free()
	var packed: PackedScene = load(SCENES[state_name])
	_current_scene = packed.instantiate()
	get_tree().root.add_child(_current_scene)
	get_tree().root.move_child(_current_scene, 0)

func _fade_out(duration: float) -> void:
	var tween := create_tween()
	tween.tween_property(_fade_rect, "color:a", 1.0, duration)
	await tween.finished

func _fade_in(duration: float) -> void:
	var tween := create_tween()
	tween.tween_property(_fade_rect, "color:a", 0.0, duration)
	await tween.finished
