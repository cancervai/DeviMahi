## WaltzRing.gd — An individual rhythm ring that pulses and shrinks toward the beat.
extends Node2D

@onready var ring_sprite: Sprite2D     = $RingSprite
@onready var shrink_ring: Sprite2D     = $ShrinkRing
@onready var label:       Label        = $GradeLabel
@onready var anim:        AnimationPlayer = $AnimationPlayer

const RING_COLOR_IDLE    := Color(0.9, 0.4, 0.55, 0.85)   ## rose pink
const RING_COLOR_PERFECT := Color(1.0, 0.95, 0.3, 1.0)    ## gold
const RING_COLOR_GOOD    := Color(0.5, 0.9, 0.8, 1.0)     ## teal
const RING_COLOR_MISS    := Color(0.5, 0.2, 0.25, 0.6)    ## dimmed crimson

var _age: float = 0.0

func _ready() -> void:
	ring_sprite.modulate   = RING_COLOR_IDLE
	shrink_ring.modulate   = Color(1, 1, 1, 0.5)
	label.text             = ""
	label.modulate.a       = 0.0
	anim.play("pulse")

func _process(delta: float) -> void:
	_age += delta
	# Shrink indicator converges toward ring over its lifetime
	var t := clampf(_age / 1.4, 0.0, 1.0)
	shrink_ring.scale = Vector2.ONE * lerpf(2.2, 1.0, t)

func play_hit(grade: String) -> void:
	match grade:
		"PERFECT": ring_sprite.modulate = RING_COLOR_PERFECT
		"GOOD":    ring_sprite.modulate = RING_COLOR_GOOD
		_:         ring_sprite.modulate = Color(1, 1, 1, 0.8)
	label.text      = grade
	label.modulate.a = 1.0
	anim.play("hit_burst")
	var tw := create_tween()
	tw.tween_property(label, "modulate:a", 0.0, 0.6).set_delay(0.4)
	tw.tween_property(self, "modulate:a", 0.0, 0.3).set_delay(0.3)

func play_miss() -> void:
	ring_sprite.modulate = RING_COLOR_MISS
	var tw := create_tween()
	tw.tween_property(self, "modulate:a", 0.0, 0.4)
