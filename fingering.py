import csv
import time
import random
import threading
import RPi.GPIO as GPIO

random.seed(42)
GPIO.setwarnings(False)
GPIO.cleanup()
GPIO.setmode(GPIO.BCM) # GPIO.BCM or GPIO.BOARD


BPMs = {
    # classical music styles
    'Largo': [40, 60],
    'Adagio': [66, 76],
    'Andante': [76, 108],
    'Moderato': [108, 120],
    'Allegro': [120, 168],
    'Presto': [168, 200],
    'Prestissimo': [200, 220],
    # modern music styles
    'Hip-Hop': [60, 100],
    'Pop': [100, 130],
    'Rock': [110, 140],
    'EDM': [120, 130],
    'Dance': [120, 130],
    'Dubstep': [140, 141],
    'Drum': [160, 180],
    'Bass': [160, 180]
}


note_to_bcm = {
    '1.': 4,
    '2.': 17,
    '3.': 18,
    '4.': 27,
    '5.': 22,
    '6.': 23,
    '7.': 24,
    "1": 25,
    "2": 5,
    "3": 6,
    "4": 12,
    "5": 13,
    "6": 19,
    "7": 16,
    "1'": 26
}


def prepare_pins():
    for pin in note_to_bcm.values():
        GPIO.setup(pin, GPIO.OUT)


def set_beat_duration(bpm_name):
    bpm_range = BPMs[bpm_name]
    bpm_value = random.randint(bpm_range[0], bpm_range[1])
    beat_duration = 60.0 / bpm_value

    return beat_duration


def accelerate(beat_duration, delta_bpm=20):
    beat_duration = beat_duration - 60.0 / delta_bpm

    return beat_duration


def ritard(beat_duration, delta_bpm=20):
    beat_duration = beat_duration + 60.0 / delta_bpm

    return beat_duration


def stroke_one_note(note, beat_duration):
    if note == "":
        time.sleep(beat_duration)
    else:
        bcm_no = note_to_bcm[note]
        if bcm_no is not None:
            # GPIO.setup(bcm_no, GPIO.OUT)
            GPIO.output(bcm_no, GPIO.HIGH)
            time.sleep(beat_duration)
            GPIO.output(bcm_no, GPIO.LOW)


def play_chord(note, beat_duration):
    chord_tones = note.split('-')
    threads = []
    for tone in chord_tones:
        thread = threading.Thread(target=stroke_one_note, args=(tone, beat_duration))
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()


def play_one_piece(sheet, bpm_name='Hip-Hop'):
    try:
        prepare_pins()
        for bar in sheet:
            print(bar)
            beat_duration = set_beat_duration(bpm_name)
            if len(bar) == 0:
                continue
            beat_duration = set_beat_duration(bpm_name)
            if bar[0].startswith('accel.'):
                delta_bpm = int(bar[0].split('-')[1])
                beat_duration = accelerate(beat_duration, delta_bpm)
                bar = bar[1:]
            elif bar[0].startswith('rit.'):
                delta_bpm = int(bar[0].split('-')[1])
                beat_duration = ritard(beat_duration, delta_bpm)
                bar = bar[1:]

            for idx, note in enumerate(bar):
                if '-' in note:
                    play_chord(note, beat_duration)
                else:
                    stroke_one_note(note, beat_duration)
    except KeyboardInterrupt:
        GPIO.cleanup()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        GPIO.cleanup()


def read_sheet_from_csv(sheet_name='FlowerSea_JayChou.csv'):
    sheet = []
    try:
        with open(sheet_name, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                sheet.append(row)
    except FileNotFoundError:
        print(f"File {sheet_name} not found.")

    return sheet


if __name__ == "__main__":
    bpm_name = 'Hip-Hop'
    sheet_name='FlowerSea_JayChou.csv'
    sheet = read_sheet_from_csv(sheet_name)
    if sheet:
        play_one_piece(sheet, bpm_name)
