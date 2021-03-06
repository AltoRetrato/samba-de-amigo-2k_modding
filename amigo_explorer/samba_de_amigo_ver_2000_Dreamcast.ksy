meta:
  # Unknown sections / elements are marked with a [?] question mark.
  id: samba_de_amigo_amg_dc
  file-extension: amg
  endian: le # alternatively, see http://doc.kaitai.io/user_guide.html#calc-endian
  title: Amigo (.AMG) file format v. 0.1, for the Sega Dreamcast game Samba de Amigo ver. 2000.
  application: Samba de Amigo ver. 2000
  ks-version: 0.8
  license: LGPL-3.0-or-later
doc: |
  Samba de Amigo ver. 2000 is a rhythm game developed by Sonic Team
  and published only in Japan by Sega for arcades and the Dreamcast.
  
  Each song in the game has a corresponding .AMG ("Amigo") file,
  with all the movements ("commands") and timing (as FPS @ 60 Hz)
  for each play mode.
  
  This file is currently a WORK IN PROGRESS!!!
seq:
  - id: blocks
    type: block
   #repeat: eos
    repeat: until
    repeat-until: '_.block_name == block_name_enum::end_'
enums:
  block_name_enum:
    0x44414548: head # 1st block
    0x5f4d4143: cam_ # camera ?
    0x59534145: easy # easy mode
    0x4d524f4e: norm # normal mode
    0x44524148: hard # hard mode
    0x52505553: supr # super hard mode
    0x455f4144: da_e # hustle easy mode
    0x4e5f4144: da_n # hustle normal mode
    0x535f4144: da_s # hustle super hard mode
    0x485f4144: da_h # hustle hard mode
    0x5f544341: act_ # actors?
   #0x48534e4f: onsh # only for the Wii version
    0x5f444e45: end_ # last block
  terminus_enum:
    0001: begin
    0002: end
types:
  block:
    seq:
      - id: block_name
        type: u4
        enum: block_name_enum
        doc: Name of the block.
      - id: block_size
        if: 'block_name != block_name_enum::end_'
        type: u4
        doc: Size of the data in the block, in bytes.
      - id: block_data
        if: 'block_name != block_name_enum::end_'
        size: block_size
        doc: Block data.
        type:
          switch-on: block_name
          cases:
            'block_name_enum::head': block_head
            'block_name_enum::easy': block_amigos
            'block_name_enum::norm': block_amigos
            'block_name_enum::hard': block_amigos
            'block_name_enum::supr': block_amigos
            'block_name_enum::da_e': block_amigos
            'block_name_enum::da_n': block_amigos
            'block_name_enum::da_s': block_amigos
            'block_name_enum::da_h': block_amigos
            'block_name_enum::cam_': block_cam_
            'block_name_enum::act_': block_act_
  block_head:
    seq:
      - id: num_entries
        type: u4
        doc: Number of entries.
      - id: entries
        type: u4
        doc: frame numbers when camera position and/or animation changes.
        repeat: expr
        repeat-expr: num_entries
  block_amigos:
    seq:
      - id: player_number
        type: u4
        doc: Player number, 0=1st player, 1=2nd player.
      - id: max_amigo_points
        type: u4
        doc: Amigo points for a perfect score.
      - id: num_commands
        type: u4
        doc: Number of commands.
      - id: commands
        type: command
        doc: Gameplay commands.
        repeat: expr
        repeat-expr: num_commands
  command:
    seq:
      - id: frame
        type: u4
        doc: Frame number for this command.
      - id: cmd_bitfield
        if: frame != 0
        type: u4
        doc: 'Bit field: bits 0-3=type, bits 4-9=position, bit 14=circle?, ...?'
    instances:
      sec:
        value: frame / 60.0
        doc: Time value in seconds @ 60 Hz.
      cmd_type:
        value: >-
          cmd_bitfield & 0xf == 1 ? "hit" :
          cmd_bitfield & 0xf == 4 ? "pose" :
          cmd_bitfield & 0xf == 3 ? "hit rapidly, begin" :
          cmd_bitfield & 0xf == 8 ? "hit rapidly, end" :
          cmd_bitfield & 0xf == 5 ? "hustle begin" :
          cmd_bitfield & 0xf == 6 ? "hustle end" :
          "unknown command"
        doc: Command type (bits 0-3).
      cmd_hustle:
        value: >-
          cmd_bitfield >> 16 & 0xf ==  0 ? "TL/TR" :
          cmd_bitfield >> 16 & 0xf ==  1 ? "BL/BR" :
          cmd_bitfield >> 16 & 0xf ==  2 ? "TL/ML" :
          cmd_bitfield >> 16 & 0xf ==  3 ? "TR/MR" :
          cmd_bitfield >> 16 & 0xf ==  4 ? "ML/BL" :
          cmd_bitfield >> 16 & 0xf ==  5 ? "MR/BR" :
          cmd_bitfield >> 16 & 0xf ==  6 ? "TL/BL" :
          cmd_bitfield >> 16 & 0xf ==  7 ? "TR/BR" :
          cmd_bitfield >> 16 & 0xf ==  8 ? "circle anti-clockwise" :
          cmd_bitfield >> 16 & 0xf ==  9 ? "circle clockwise" :
          cmd_bitfield >> 16 & 0xf == 10 ? "TL/TR" :
          cmd_bitfield >> 16 & 0xf == 11 ? "BL/BR" :
          cmd_bitfield >> 16 & 0xf == 12 ? "TL/TR" :
          cmd_bitfield >> 16 & 0xf == 13 ? "BL/BR" :
          cmd_bitfield >> 16 & 0xf == 14 ? "TL/TR 2 hands" :
          cmd_bitfield >> 16 & 0xf == 15 ? "BL/BR 2 hands" :
          "unknown command"
        doc: Hustle command.
      cmd_pos:
        value: >-
          [cmd_bitfield >> 4 & 1 == 1 ? "TL" : "",
           cmd_bitfield >> 5 & 1 == 1 ? "ML" : "",
           cmd_bitfield >> 6 & 1 == 1 ? "BL" : "",
           cmd_bitfield >> 7 & 1 == 1 ? "TR" : "",
           cmd_bitfield >> 8 & 1 == 1 ? "MR" : "",
           cmd_bitfield >> 9 & 1 == 1 ? "BR" : ""]
        doc: Command position (bits 4-9).
      cmd_hustle_bits:
        value: >-
          cmd_bitfield >> 16 & 0xf ==  0 ? "TL/TR" :
          cmd_bitfield >> 16 & 0xf ==  1 ? "BL/BR" :
          cmd_bitfield >> 16 & 0xf ==  2 ? "TL/ML" :
          cmd_bitfield >> 16 & 0xf ==  3 ? "TR/MR" :
          cmd_bitfield >> 16 & 0xf ==  4 ? "ML/BL" :
          cmd_bitfield >> 16 & 0xf ==  5 ? "MR/BR" :
          cmd_bitfield >> 16 & 0xf ==  6 ? "TL/BL" :
          cmd_bitfield >> 16 & 0xf ==  7 ? "TR/BR" :
          cmd_bitfield >> 16 & 0xf ==  8 ? "circle anti-clockwise" :
          cmd_bitfield >> 16 & 0xf ==  9 ? "circle clockwise" :
          cmd_bitfield >> 16 & 0xf == 10 ? "TL/TR" :
          cmd_bitfield >> 16 & 0xf == 11 ? "BL/BR" :
          cmd_bitfield >> 16 & 0xf == 12 ? "TL/TR" :
          cmd_bitfield >> 16 & 0xf == 13 ? "BL/BR" :
          cmd_bitfield >> 16 & 0xf == 14 ? "TL/TR 2 hands" :
          cmd_bitfield >> 16 & 0xf == 15 ? "BL/BR 2 hands" :
          "unknown hustle command"
        doc: Hustle command (bits 16-19).
      cmd_reserved_bits:
        value: 'cmd_bitfield >> 20' # bits 20-31
        doc: Unused / reserved.
  block_cam_:
    seq:
      - id: num_entries
        type: u4
        doc: Number of entries.
      - id: entries
        type: cam_data
        doc: Camera data?
        repeat: expr
        repeat-expr: num_entries
  cam_data:
    seq:
      - id: frame
        type: u4
        doc: Frame number.
      - id: terminus
        type: u2
        enum: terminus_enum
        doc: Either BEGIN(ning) or END of a camera transition? Changing this value doesn't change anything?
      - id: transition_speed
        type: u2
        doc: The larger this value, the slower is the transition speed.
      - id: camera_x
        type: s4
        doc: Camera position, X axis.
      - id: camera_y
        type: s4
        doc: Camera position, Y axis.
      - id: camera_z
        type: s4
        doc: Camera position, Z axis. Negative values go into the screen.
      - id: target_x
        type: s4
        doc: Camera target position, X axis.
      - id: target_y
        type: s4
        doc: Camera target position, Y axis.
      - id: target_z
        type: s4
        doc: Camera target position, Z axis.
  block_act_:
    seq:
      - id: act_num
        type: u4
        doc: Act number.(?)
      - id: num_entries
        type: u4
        doc: Number of entries.
      - id: entries
        type: act_data
        doc: Act data?
        repeat: expr
        repeat-expr: num_entries
  act_data:
    seq:
      - id: frame
        type: u4
        doc: Frame number.
      - id: dance_move
        type: u1
        doc: Actor dance move (range from 0x01 to 0x0C).
      - id: dance_speed
        type: u1
        doc: Dance speed? (larger values provide faster animation, varies between 0x00 and 0x10).
      - id: cycle_size
        type: u2
        doc: Animation cycle size? (larger values means slower and/or longer animation cycle?)
      - id: actor_x
        type: s2
        doc: Actor position, X axis.
      - id: actor_y
        type: s2
        doc: Actor position, Y axis? But doesn't seem to be used...
      - id: actor_z
        type: s2
        doc: Actor position, Z axis. Positive values move actor away from camera?
      - id: unknown
        type: s2
        doc: Unknown function. Either 0000, 0113, 0115, or FFFF.
