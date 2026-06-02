## MainMenu.gd — Gothic title screen with animated candle flicker.
extends Node2D

@onready var title_label:  Label       = $UI/TitleLabel
@onready var start_btn:    Button      = $UI/StartButton
@onready var load_btn:     Button      = $UI/LoadButton
@onready var quit_btn:     Button      = $UI/QuitButton
@onready var candles:      Node2D      = $CandleLayer
@onready var anim_player:  AnimationPlayer = $AnimationPlayer

func _ready() -> void:
	start_btn.pressed.connect(_on_start)
	load_btn.pressed.connect(_on_load)
	quit_btn.pressed.connect(_on_quit)
	anim_player.play("intro_fade")

func _process(delta: float) -> void:
	# Flicker candle lights
	for candle in candles.get_children():
		var flicker := randf_range(0.75, 1.0)
		if candle.has_node("PointLight2D"):
			candle.get_node("PointLight2D").energy = flicker

func _on_start() -> void:
	StateManager.goto("act1_citadel")

func _on_load() -> void:
	Global.load_game()
	StateManager.goto("act%d_citadel" % Global.current_act if Global.current_act == 1 else "act2_swamp")

func _on_quit() -> void:
	get_tree().quit()
