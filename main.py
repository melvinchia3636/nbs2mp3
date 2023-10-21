from midiutil import MIDIFile
from midi2audio import FluidSynth
import os
import json

TARGET = "./media/nbs/daoxiang.nbs"

# 0 = Piano (Air)
# 1 = Double Bass (Wood)
# 2 = Bass Drum (Stone)
# 3 = Snare Drum (Sand)
# 4 = Click (Glass)
# 5 = Guitar (Wool)
# 6 = Flute (Clay)
# 7 = Bell (Block of Gold)
# 8 = Chime (Packed Ice)
# 9 = Xylophone (Bone Block)
# 10 = Iron Xylophone (Iron Block)
# 11 = Cow Bell (Soul Sand)
# 12 = Didgeridoo (Pumpkin)
# 13 = Bit (Block of Emerald)
# 14 = Banjo (Hay)
# 15 = Pling (Glowstone)
MIDI_PROGRAM_LIST = {
    0: 1,
    1: 33,
    2: 118,
    3: 118,
    4: 113,
    5: 25,
    6: 75,
    7: 14,
    8: 15,
    9: 14,
    10: 14,
    11: 14,
    12: 14,
    13: 14,
    14: 14,
    15: 14,
}


def read_byte(file):
    return int.from_bytes(file.read(1), byteorder='little')


def read_short(file):
    return int.from_bytes(file.read(2), byteorder='little')


def read_int(file):
    return int.from_bytes(file.read(4), byteorder='little')


def read_string(file):
    length = read_int(file)
    return file.read(length).decode('utf-8')


data = {}


def set_note(layer, tick, instrument, note):
    if layer not in data:
        data[layer] = {}

    if tick not in data[layer]:
        data[layer][tick] = {}

    data[layer][tick] = [instrument, note]


with open(TARGET, "rb") as file:
    nothing = read_short(file)
    if nothing == 0:
        version = read_byte(file)
        vanilla_instrument_count = read_byte(file)
        song_length = read_short(file)
        layer_count = read_short(file)
        song_name = read_string(file)
        song_author = read_string(file)
        song_original_author = read_string(file)
        song_description = read_string(file)
        song_tempo = read_short(file)
        auto_save = read_byte(file)
        auto_save_duration = read_byte(file)
        time_signature = read_byte(file)
        minutes_spent = read_int(file)
        left_clicks = read_int(file)
        right_clicks = read_int(file)
        noteblocks_added = read_int(file)
        noteblocks_removed = read_int(file)
        midi_schematic_filename = read_string(file)
        read_byte(file)
        read_byte(file)
        read_short(file)
    else:
        song_height = read_short(file)
        song_name = read_string(file)
        song_author = read_string(file)
        song_original_author = read_string(file)
        song_description = read_string(file)
        song_tempo = read_short(file)
        auto_save = read_byte(file)
        auto_save_duration = read_byte(file)
        time_signature = read_byte(file)
        minutes_spent = read_int(file)
        left_clicks = read_int(file)
        right_clicks = read_int(file)
        blocks_added = read_int(file)
        blocks_removed = read_int(file)
        midi_schematic_filename = read_string(file)

    tick = -1
    while True:
        jump_ticks = read_short(file)

        if jump_ticks == 0:
            break

        tick += jump_ticks

        layer = -1

        while True:
            jump_layers = read_short(file)
            if (jump_layers > 100):
                print(jump_layers)

            if jump_layers == 0:
                break

            layer += jump_layers

            set_note(layer, tick, read_byte(file), read_byte(file))

            if nothing == 0:
                read_byte(file)
                read_byte(file)
                read_short(file)

midi = MIDIFile(layer_count if nothing ==
                0 else song_height if song_height != 0 else max(data.keys()) + 1)
midi.addTempo(0, 0, song_tempo / 2)


last_instrument = None
for layer in data:

    for tick in data[layer]:
        midi.addProgramChange(
            layer,
            0,
            tick,
            data[layer][tick][0]
        )
        last_instrument = data[layer][tick][0]

        midi.addNote(
            layer,
            0,
            data[layer][tick][1] + 12,
            tick,
            0.5,
            100
        )

with open("output.mid", "wb") as output_file:
    midi.writeFile(output_file)

json.dump(data, open('data.json', 'w'), indent=2)

FluidSynth('./sf4.sf2').midi_to_audio('./output.mid', './output.wav')
os.remove('./output.mid')
os.system('ffmpeg -i output.wav -acodec libmp3lame -ab 320k output.mp3')
os.remove('./output.wav')
os.rename('./output.mp3', TARGET.replace('.nbs', '.mp3'))
