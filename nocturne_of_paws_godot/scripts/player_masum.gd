## PlayerMasum.gd — Midnight-black cat protagonist with mobile touch controls.
##
## Movement: virtual joystick for walk/run, tap for jump/interact.
## Physics: CharacterBody2D with variable jump, coyote time, jump buffering.
extends CharacterBody2D

# ── Constants ─────────────────────────────────────────────────────────────────
const WALK_SPEED    := 80.0
const RUN_SPEED     := 150.0
const JUMP_VELOCITY := -260.0
const GRAVITY       := 980.0
const COYOTE_TIME   := 0.12
const JUMP_BUFFER   := 0.14

# ── Cuddle mechanic ───────────────────────────────────────────────────────────
const HOLD_THRESHOLD := 0.8          ## seconds before cuddle triggers
const CUDDLE_ZOOM    := 0.75         ## Camera zoom-out target

# ── Nodes ─────────────────────────────────────────────────────────────────────
@onready var anim: AnimatedSprite2D    = $AnimatedSprite2D
@onready var camera: Camera2D          = $Camera2D
@onready var hold_label: Label         = $HoldLabel
@onready var tail_anim: AnimatedSprite2D = $TailAnimation

# ── Touch state ───────────────────────────────────────────────────────────────
var _joystick_origin: Vector2 = Vector2.ZERO
var _joystick_vec: Vector2    = Vector2.ZERO
var _joystick_touch_idx: int  = -1
var _hold_timer: float        = 0.0
var _is_holding: bool         = false
var _cuddling: bool           = false
var _at_vista: bool           = false    ## set by trigger area

# ── Physics state ─────────────────────────────────────────────────────────────
var _coyote_timer: float  = 0.0
var _jump_buffer: float   = 0.0
var _was_on_floor: bool   = false

# ── Signals ───────────────────────────────────────────────────────────────────
signal cuddle_started
signal cuddle_ended
signal jumped

func _ready() -> void:
	hold_label.visible = false
	tail_anim.visible  = false
	camera.position_smoothing_enabled = true
	camera.position_smoothing_speed   = 6.0
	camera.zoom = Vector2(2.0, 2.0)   ## 2× pixel zoom for 8-bit crispness

# ─────────────────────────────────────────────────────────────────────────────

func _physics_process(delta: float) -> void:
	_process_timers(delta)
	_apply_gravity(delta)
	_handle_movement(delta)
	_handle_jump()
	_handle_hold_cuddle(delta)
	move_and_slide()
	_update_animation()

func _input(event: InputEvent) -> void:
	# ── Virtual joystick (left half of screen) ────────────────────────────────
	if event is InputEventScreenTouch:
		if event.pressed and event.position.x < get_viewport().get_visible_rect().size.x * 0.5:
			_joystick_touch_idx = event.index
			_joystick_origin    = event.position
			_joystick_vec       = Vector2.ZERO
		elif not event.pressed and event.index == _joystick_touch_idx:
			_joystick_touch_idx = -1
			_joystick_vec       = Vector2.ZERO

	elif event is InputEventScreenDrag and event.index == _joystick_touch_idx:
		var delta_vec := event.position - _joystick_origin
		_joystick_vec = delta_vec.limit_length(40.0) / 40.0

	# ── Jump tap (right half of screen) ──────────────────────────────────────
	if event is InputEventScreenTouch and event.pressed:
		if event.position.x > get_viewport().get_visible_rect().size.x * 0.5:
			_jump_buffer = JUMP_BUFFER

	# ── Hold anywhere (cuddle trigger) ────────────────────────────────────────
	if event is InputEventScreenTouch:
		if event.pressed and _at_vista:
			_is_holding = true
		elif not event.pressed:
			_is_holding = false
			if _cuddling:
				_end_cuddle()

# ── Physics helpers ───────────────────────────────────────────────────────────

func _process_timers(delta: float) -> void:
	_jump_buffer  = maxf(0.0, _jump_buffer  - delta)
	_coyote_timer = maxf(0.0, _coyote_timer - delta)

	if _was_on_floor and not is_on_floor():
		_coyote_timer = COYOTE_TIME
	_was_on_floor = is_on_floor()

func _apply_gravity(delta: float) -> void:
	if not is_on_floor():
		velocity.y += GRAVITY * delta
		velocity.y  = minf(velocity.y, 800.0)
	else:
		velocity.y = 0.0

func _handle_movement(_delta: float) -> void:
	var dx := _joystick_vec.x
	var speed := RUN_SPEED if abs(dx) > 0.75 else WALK_SPEED
	velocity.x = dx * speed

	if dx != 0:
		anim.flip_h = dx < 0

func _handle_jump() -> void:
	if _jump_buffer > 0 and (is_on_floor() or _coyote_timer > 0):
		velocity.y    = JUMP_VELOCITY
		_jump_buffer  = 0.0
		_coyote_timer = 0.0
		emit_signal("jumped")

# ── Hold-to-Cuddle ────────────────────────────────────────────────────────────

func _handle_hold_cuddle(delta: float) -> void:
	if not _at_vista:
		hold_label.visible = false
		return

	hold_label.visible = not _cuddling

	if _is_holding and not _cuddling:
		_hold_timer += delta
		if _hold_timer >= HOLD_THRESHOLD:
			_start_cuddle()
	elif not _is_holding:
		_hold_timer = 0.0

func _start_cuddle() -> void:
	_cuddling  = true
	_hold_timer = 0.0
	tail_anim.visible = true
	tail_anim.play("wrap")
	# Smooth cinematic zoom-out
	var tween := create_tween()
	tween.tween_property(camera, "zoom",
		Vector2(CUDDLE_ZOOM, CUDDLE_ZOOM), 1.2).set_trans(Tween.TRANS_SINE)
	# Fade HUD
	emit_signal("cuddle_started")

func _end_cuddle() -> void:
	_cuddling = false
	tail_anim.visible = false
	var tween := create_tween()
	tween.tween_property(camera, "zoom", Vector2(2.0, 2.0), 0.8).set_trans(Tween.TRANS_SINE)
	emit_signal("cuddle_ended")

# ── Vista trigger ─────────────────────────────────────────────────────────────

func set_at_vista(value: bool) -> void:
	_at_vista = value
	if not value and _cuddling:
		_end_cuddle()

# ── Animation ─────────────────────────────────────────────────────────────────

func _update_animation() -> void:
	if _cuddling:
		anim.play("cuddle_sit")
	elif not is_on_floor():
		anim.play("jump")
	elif abs(velocity.x) > RUN_SPEED * 0.6:
		anim.play("run")
	elif abs(velocity.x) > 2:
		anim.play("walk")
	else:
		anim.play("idle")
