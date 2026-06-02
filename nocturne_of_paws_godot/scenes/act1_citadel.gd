## Act1Citadel.gd — Obsidian Citadel scene controller.
## Wires player → companion, vista triggers, checkpoint waltz activation,
## and cuddle dialogue sequences.
extends Node2D

@onready var player:        CharacterBody2D  = $PlayerMasum
@onready var companion:     CharacterBody2D  = $CompanionMahi
@onready var dialogue:      CanvasLayer      = $DialogueBox
@onready var touch_ui:      CanvasLayer      = $TouchControls
@onready var oxytocin_ui:   CanvasLayer      = $OxytocinMeter
@onready var camera:        Camera2D         = $PlayerMasum/Camera2D
@onready var wind_particles: GPUParticles2D  = $WindParticles

# ── Waltz checkpoint areas (Area2D nodes in the scene) ───────────────────────
@onready var waltz_checkpoints: Array = $WaltzCheckpoints.get_children()
@onready var vista_zones:       Array = $VistaZones.get_children()

# ── Cuddle dialogue lines ─────────────────────────────────────────────────────
const CUDDLE_LINES := [
	{"speaker": "Mahi",  "text": "The mist swallows the stars whole tonight..."},
	{"speaker": "Masum", "text": "Then we are the only light left in it."},
	{"speaker": "Mahi",  "text": "Hold me a little longer."},
	{"speaker": "Masum", "text": "Until dawn forgets to come."},
]

const WIND_LINES := [
	{"speaker": "Mahi",  "text": "Something cold moves through the corridors..."},
	{"speaker": "Masum", "text": "Stay close."},
]

func _ready() -> void:
	# Wire touch input to player
	touch_ui.axis_changed.connect(func(v): player._joystick_vec = v)
	touch_ui.jump_pressed.connect(func(): player._jump_buffer = 0.14)
	touch_ui.interact_pressed.connect(_on_interact)

	# Wire companion target
	companion.set_target(player)

	# Wire cuddle signals
	player.cuddle_started.connect(_on_cuddle_started)
	player.cuddle_ended.connect(_on_cuddle_ended)

	# Wire vista zones
	for zone in vista_zones:
		zone.body_entered.connect(func(b): if b == player: player.set_at_vista(true))
		zone.body_exited.connect(func(b):  if b == player: player.set_at_vista(false))

	# Wire waltz checkpoints
	for cp in waltz_checkpoints:
		cp.body_entered.connect(_on_waltz_checkpoint.bind(cp))

	# Wire wind hazard (random trigger)
	_schedule_wind()

	# Opening dialogue
	dialogue.queue_lines([
		{"speaker": "Masum", "text": "...The Citadel smells of old roses and iron."},
		{"speaker": "Mahi",  "text": "Stay close. The corridors remember those who wander."},
	])

# ── Cuddle ────────────────────────────────────────────────────────────────────

func _on_cuddle_started() -> void:
	# Fade out touch controls
	var tw := create_tween()
	tw.tween_property(touch_ui, "modulate:a", 0.0, 0.6)
	# Queue cuddle dialogue (with delay)
	await get_tree().create_timer(1.2).timeout
	dialogue.queue_lines(CUDDLE_LINES)

func _on_cuddle_ended() -> void:
	var tw := create_tween()
	tw.tween_property(touch_ui, "modulate:a", 1.0, 0.4)

# ── Waltz checkpoint ──────────────────────────────────────────────────────────

func _on_waltz_checkpoint(cp: Area2D) -> void:
	if not cp.get_meta("triggered", false):
		cp.set_meta("triggered", true)
		StateManager.push("waltz_game")

# ── Wind hazard ───────────────────────────────────────────────────────────────

func _schedule_wind() -> void:
	await get_tree().create_timer(randf_range(15.0, 30.0)).timeout
	_trigger_wind()

func _trigger_wind() -> void:
	wind_particles.emitting = true
	companion._hazard_nearby = true
	dialogue.queue_lines(WIND_LINES)
	await get_tree().create_timer(3.0).timeout
	wind_particles.emitting  = false
	companion._hazard_nearby = false
	_schedule_wind()

# ── Interact ──────────────────────────────────────────────────────────────────

func _on_interact() -> void:
	pass   ## expanded per NPC / object in later sprints
