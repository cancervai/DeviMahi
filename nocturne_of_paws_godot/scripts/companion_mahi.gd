## CompanionMahi.gd — Ethereal white cat companion with mobile pathfinding.
##
## Mahi follows Masum using NavigationAgent2D for intelligent obstacle avoidance.
## She presses against Masum automatically when hazards are detected.
extends CharacterBody2D

# ── Constants ─────────────────────────────────────────────────────────────────
const FOLLOW_SPEED       := 90.0
const CLOSE_DISTANCE     := 12.0     ## pixels — considered "beside" Masum
const SNUGGLE_DISTANCE   := 6.0      ## triggers snuggle-press animation
const HOVER_AMPLITUDE    := 1.5      ## ethereal bob (pixels)
const HOVER_FREQUENCY    := 2.8
const HAZARD_CLOSE_SPEED := 160.0    ## rush speed when hazard detected

# ── Nodes ─────────────────────────────────────────────────────────────────────
@onready var anim: AnimatedSprite2D         = $AnimatedSprite2D
@onready var nav: NavigationAgent2D         = $NavigationAgent2D
@onready var glow: PointLight2D             = $GlowLight
@onready var hazard_detector: Area2D        = $HazardDetector

# ── State ─────────────────────────────────────────────────────────────────────
var _target: CharacterBody2D = null
var _hazard_nearby: bool     = false
var _timer: float            = 0.0
var _snuggling: bool         = false

# ── Signals ───────────────────────────────────────────────────────────────────
signal snuggled_against_player

func _ready() -> void:
	nav.path_desired_distance       = 4.0
	nav.target_desired_distance     = CLOSE_DISTANCE
	nav.avoidance_enabled           = true
	hazard_detector.body_entered.connect(_on_hazard_entered)
	hazard_detector.body_exited.connect(_on_hazard_exited)

func set_target(player: CharacterBody2D) -> void:
	_target = player

# ─────────────────────────────────────────────────────────────────────────────

func _physics_process(delta: float) -> void:
	_timer += delta
	if _target == null:
		return

	_update_navigation(delta)
	_apply_hover(delta)
	move_and_slide()
	_update_glow()
	_update_animation()

func _update_navigation(delta: float) -> void:
	var dist := global_position.distance_to(_target.global_position)
	var speed := HAZARD_CLOSE_SPEED if _hazard_nearby else FOLLOW_SPEED

	# Don't crowd Masum unless hazard forces it
	if dist < SNUGGLE_DISTANCE and not _hazard_nearby:
		velocity = Vector2.ZERO
		if not _snuggling:
			_snuggling = true
			emit_signal("snuggled_against_player")
		return
	_snuggling = false

	nav.target_position = _target.global_position
	if nav.is_navigation_finished():
		velocity = Vector2.ZERO
		return

	var next      := nav.get_next_path_position()
	var direction := (next - global_position).normalized()
	velocity       = direction * speed

	if velocity.x != 0:
		anim.flip_h = velocity.x < 0

func _apply_hover(_delta: float) -> void:
	# Ethereal sine-wave vertical hover (cosmetic only, not physics)
	var hover_offset := sin(_timer * HOVER_FREQUENCY) * HOVER_AMPLITUDE
	position.y += hover_offset * 0.016   ## small nudge per frame, not delta-scaled

func _update_glow() -> void:
	# Glow pulses with Mahi's bond level
	var pulse := 0.8 + 0.2 * sin(_timer * 3.0)
	glow.energy = pulse * (0.5 + Global.oxytocin_level / 200.0)

func _update_animation() -> void:
	if _snuggling:
		anim.play("snuggle")
	elif _hazard_nearby:
		anim.play("press")
	elif velocity.length() > 5:
		anim.play("walk")
	else:
		anim.play("idle_float")

# ── Hazard detection ──────────────────────────────────────────────────────────

func _on_hazard_entered(_body: Node) -> void:
	_hazard_nearby = true

func _on_hazard_exited(_body: Node) -> void:
	_hazard_nearby = false
