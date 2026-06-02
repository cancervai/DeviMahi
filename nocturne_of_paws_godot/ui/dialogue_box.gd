## DialogueBox.gd — Gothic typewriter dialogue with speaker portrait.
## Fades in during cuddle / emotional moments.
extends CanvasLayer

const CHARS_PER_SEC := 30.0
const FADE_SPEED    := 2.0

@onready var box:          PanelContainer = $Box
@onready var speaker_lbl:  Label          = $Box/VBox/Speaker
@onready var body_lbl:     Label          = $Box/VBox/Body
@onready var continue_ind: Label          = $Box/ContinueIndicator
@onready var tween_node:   Tween          = null

var _queue:        Array[Dictionary] = []
var _visible_chars: float = 0.0
var _full_text:    String = ""
var _active:       bool   = false
var _done:         bool   = false

signal dialogue_finished

func _ready() -> void:
	box.modulate.a = 0.0

func queue_lines(lines: Array[Dictionary]) -> void:
	## lines: [{"speaker": "Masum", "text": "..."}, ...]
	_queue.append_array(lines)
	if not _active:
		_advance()

func _advance() -> void:
	if _queue.is_empty():
		_active = false
		_fade_box(0.0)
		emit_signal("dialogue_finished")
		return
	var line    := _queue.pop_front() as Dictionary
	_full_text   = line.get("text", "")
	speaker_lbl.text    = line.get("speaker", "")
	body_lbl.visible_characters = 0
	body_lbl.text       = _full_text
	_visible_chars      = 0.0
	_done               = false
	_active             = true
	_fade_box(1.0)

func _process(delta: float) -> void:
	if not _active or _done:
		return
	_visible_chars = minf(_visible_chars + CHARS_PER_SEC * delta, float(len(_full_text)))
	body_lbl.visible_characters = int(_visible_chars)
	if _visible_chars >= float(len(_full_text)):
		_done = true
		continue_ind.visible = true

func _input(event: InputEvent) -> void:
	if not _active:
		return
	var tapped := event is InputEventScreenTouch and (event as InputEventScreenTouch).pressed
	var entered := event is InputEventKey and (event as InputEventKey).keycode == KEY_ENTER \
	               and (event as InputEventKey).pressed
	if tapped or entered:
		if not _done:
			_visible_chars = float(len(_full_text))
		else:
			continue_ind.visible = false
			_advance()

func _fade_box(target_alpha: float) -> void:
	if tween_node:
		tween_node.kill()
	tween_node = create_tween()
	tween_node.tween_property(box, "modulate:a", target_alpha, 1.0 / FADE_SPEED)
