## WaltzGame.gd — Mobile Touch-Waltz rhythm minigame.
##
## Glowing rings appear at random screen positions. Player must tap inside
## each ring within the beat window. Successful taps spawn pink star particles
## and trigger Masum+Mahi twirl animations. Boosts oxytocin on combos.
extends Node2D

# ── Constants ─────────────────────────────────────────────────────────────────
const BPM          := 96.0
const BEAT_SECONDS := 60.0 / BPM
const RING_SPAWN_R := 28.0    ## ring visual radius (pixels at native res)
const HIT_WINDOW   := 0.22    ## seconds of leniency around the beat
const RING_LIFETIME := 1.4    ## how long a ring lives before missing

# ── Score thresholds ──────────────────────────────────────────────────────────
const PERFECT_DIST := 8.0
const GOOD_DIST    := 18.0

# ── Nodes ─────────────────────────────────────────────────────────────────────
@onready var rings_layer:   Node2D          = $RingsLayer
@onready var particles:     GPUParticles2D  = $StarParticles
@onready var anim_masum:    AnimatedSprite2D = $Characters/Masum
@onready var anim_mahi:     AnimatedSprite2D = $Characters/Mahi
@onready var score_label:   Label           = $HUD/ScoreLabel
@onready var combo_label:   Label           = $HUD/ComboLabel
@onready var beat_flash:    ColorRect        = $BeatFlash

# ── Ring scene ────────────────────────────────────────────────────────────────
const RingScene := preload("res://scenes/waltz_ring.tscn")

# ── State ─────────────────────────────────────────────────────────────────────
var _timer:      float = 0.0
var _beat_timer: float = 0.0
var _score:      int   = 0
var _combo:      int   = 0
var _misses:     int   = 0
var _rings:      Array = []

# Viewport size cached for spawn positioning
var _vp_size: Vector2

func _ready() -> void:
	_vp_size = get_viewport().get_visible_rect().size
	beat_flash.color.a = 0.0
	anim_masum.play("waltz_idle")
	anim_mahi.play("waltz_idle")
	particles.emitting = false

func _process(delta: float) -> void:
	_timer      += delta
	_beat_timer += delta

	_pulse_beat_flash(delta)

	if _beat_timer >= BEAT_SECONDS:
		_beat_timer -= BEAT_SECONDS
		_spawn_ring()
		_on_beat_flash()

	_age_rings(delta)

func _input(event: InputEvent) -> void:
	if event is InputEventScreenTouch and (event as InputEventScreenTouch).pressed:
		_check_tap((event as InputEventScreenTouch).position)

# ── Ring lifecycle ────────────────────────────────────────────────────────────

func _spawn_ring() -> void:
	var margin := RING_SPAWN_R + 10.0
	var pos := Vector2(
		randf_range(margin, _vp_size.x - margin),
		randf_range(margin * 2, _vp_size.y - margin)
	)
	var ring: Node2D = RingScene.instantiate()
	ring.position = pos
	rings_layer.add_child(ring)
	_rings.append({"node": ring, "pos": pos, "age": 0.0, "hit": false})

func _age_rings(delta: float) -> void:
	var to_remove: Array = []
	for r in _rings:
		r["age"] += delta
		if not r["hit"] and r["age"] > RING_LIFETIME:
			_miss(r)
			to_remove.append(r)
		elif r["hit"] and r["age"] > RING_LIFETIME + 0.4:
			to_remove.append(r)
	for r in to_remove:
		r["node"].queue_free()
		_rings.erase(r)

func _miss(ring_data: Dictionary) -> void:
	_misses += 1
	_combo   = 0
	ring_data["node"].play_miss()
	_update_hud()

# ── Tap detection ─────────────────────────────────────────────────────────────

func _check_tap(touch_pos: Vector2) -> void:
	var best_ring = null
	var best_dist := INF

	for r in _rings:
		if r["hit"]:
			continue
		var dist := touch_pos.distance_to(r["pos"])
		if dist < RING_SPAWN_R + 10.0 and dist < best_dist:
			best_dist = dist
			best_ring = r

	if best_ring == null:
		_combo = 0
		_update_hud()
		return

	best_ring["hit"] = true
	var grade: String
	if best_dist <= PERFECT_DIST:
		grade = "PERFECT"
		_score += 100 + _combo * 10
		_combo  += 1
		Global.add_oxytocin(2.0 + _combo * 0.5)
	elif best_dist <= GOOD_DIST:
		grade = "GOOD"
		_score += 50 + _combo * 5
		_combo  += 1
		Global.add_oxytocin(1.0)
	else:
		grade = "OK"
		_score += 20
		_combo  = maxf(0, _combo - 1)

	best_ring["node"].play_hit(grade)
	_spawn_stars(best_ring["pos"])
	_trigger_twirl()
	_update_hud()

# ── Reactions ─────────────────────────────────────────────────────────────────

func _spawn_stars(at: Vector2) -> void:
	particles.global_position = at
	particles.restart()
	particles.emitting = true

func _trigger_twirl() -> void:
	anim_masum.play("waltz_twirl")
	anim_mahi.play("waltz_twirl")
	await get_tree().create_timer(0.5).timeout
	anim_masum.play("waltz_idle")
	anim_mahi.play("waltz_idle")

func _on_beat_flash() -> void:
	beat_flash.color.a = 0.18
	var tw := create_tween()
	tw.tween_property(beat_flash, "color:a", 0.0, 0.25)

func _pulse_beat_flash(_delta: float) -> void:
	pass  ## handled by tween above

# ── HUD ───────────────────────────────────────────────────────────────────────

func _update_hud() -> void:
	score_label.text = "Score: %d" % _score
	combo_label.text = "x%d" % _combo if _combo > 1 else ""
