## TouchControls.gd — On-screen virtual joystick + action buttons.
##
## Left half: analogue joystick (floating origin — spawns wherever you touch).
## Right half: Jump button + Interact button.
## Emits signals consumed by PlayerMasum.
extends CanvasLayer

# ── Nodes ─────────────────────────────────────────────────────────────────────
@onready var joystick_bg:    TextureRect = $Joystick/Background
@onready var joystick_knob:  TextureRect = $Joystick/Knob
@onready var btn_jump:       TouchScreenButton = $RightPanel/JumpButton
@onready var btn_interact:   TouchScreenButton = $RightPanel/InteractButton

# ── Signals (consumed by player) ─────────────────────────────────────────────
signal axis_changed(vec: Vector2)
signal jump_pressed
signal interact_pressed

# ── Constants ─────────────────────────────────────────────────────────────────
const DEAD_ZONE    := 0.15
const JOYSTICK_R   := 40.0     ## max knob travel in pixels

# ── State ─────────────────────────────────────────────────────────────────────
var _touch_idx:    int     = -1
var _origin:       Vector2 = Vector2.ZERO
var _current_axis: Vector2 = Vector2.ZERO

func _ready() -> void:
	joystick_bg.visible  = false
	joystick_knob.visible = false
	btn_jump.pressed.connect(func(): emit_signal("jump_pressed"))
	btn_interact.pressed.connect(func(): emit_signal("interact_pressed"))

func _input(event: InputEvent) -> void:
	var half_w := get_viewport().get_visible_rect().size.x * 0.5

	if event is InputEventScreenTouch:
		var touch := event as InputEventScreenTouch
		if touch.position.x < half_w:
			if touch.pressed:
				_touch_idx            = touch.index
				_origin               = touch.position
				joystick_bg.global_position  = _origin - joystick_bg.size * 0.5
				joystick_knob.global_position = _origin - joystick_knob.size * 0.5
				joystick_bg.visible   = true
				joystick_knob.visible = true
			elif touch.index == _touch_idx:
				_release_joystick()

	elif event is InputEventScreenDrag:
		var drag := event as InputEventScreenDrag
		if drag.index == _touch_idx:
			var delta := drag.position - _origin
			var clamped := delta.limit_length(JOYSTICK_R)
			joystick_knob.global_position = _origin + clamped - joystick_knob.size * 0.5
			var axis := clamped / JOYSTICK_R
			if axis.length() < DEAD_ZONE:
				axis = Vector2.ZERO
			if axis != _current_axis:
				_current_axis = axis
				emit_signal("axis_changed", axis)

func _release_joystick() -> void:
	_touch_idx    = -1
	_current_axis = Vector2.ZERO
	joystick_bg.visible   = false
	joystick_knob.visible = false
	emit_signal("axis_changed", Vector2.ZERO)
