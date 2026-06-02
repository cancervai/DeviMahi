## OxytocinMeter.gd — Pulsing heart bond bar anchored to top-right corner.
## Listens to Global.oxytocin_changed and tweens the bar fill.
extends CanvasLayer

@onready var fill_bar:   TextureProgressBar = $Meter/FillBar
@onready var heart_icon: AnimatedSprite2D   = $Meter/HeartIcon
@onready var label:      Label              = $Meter/Label

var _display_value: float = 0.0
var _tween: Tween         = null

const PULSE_SPEED := 2.5

func _ready() -> void:
	Global.oxytocin_changed.connect(_on_oxytocin_changed)
	fill_bar.min_value = 0.0
	fill_bar.max_value = 100.0
	fill_bar.value     = Global.oxytocin_level
	_display_value     = Global.oxytocin_level

func _process(delta: float) -> void:
	# Smooth bar fill
	_display_value = lerpf(_display_value, Global.oxytocin_level, delta * 5.0)
	fill_bar.value = _display_value
	label.text     = "%d%%" % int(_display_value)

	# Heartbeat pulse on the icon
	var pulse := 1.0 + 0.08 * sin(Time.get_ticks_msec() * 0.001 * PULSE_SPEED)
	heart_icon.scale = Vector2(pulse, pulse)

func _on_oxytocin_changed(new_value: float) -> void:
	if new_value > _display_value:
		_flash_pulse()

func _flash_pulse() -> void:
	if _tween:
		_tween.kill()
	_tween = create_tween()
	_tween.tween_property(heart_icon, "modulate",
		Color(1.5, 0.8, 0.9), 0.1)
	_tween.tween_property(heart_icon, "modulate",
		Color(1.0, 1.0, 1.0), 0.3)
