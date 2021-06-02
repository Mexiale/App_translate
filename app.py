import argparse
import os
import queue
import sounddevice as sd
import vosk
import sys
import json
import pyttsx3


q = queue.Queue()

#Parametre de la voie
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('rate', 120)

def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text

def callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))

# Demande du model a utilisé
answer = str(input('Quelle langue dois-je écouté ? '))

def run(res):
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(
        '-l', '--list-devices', action='store_true',
        help='show list of audio devices and exit')
    args, remaining = parser.parse_known_args()
    if args.list_devices:
        print(sd.query_devices())
        parser.exit(0)
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=[parser])
    parser.add_argument(
        '-f', '--filename', type=str, metavar='FILENAME',
        help='audio file to store recording to')
    parser.add_argument(
        '-m', '--model', type=str, metavar='MODEL_PATH',
        help='Path to the model')
    parser.add_argument(
        '-d', '--device', type=int_or_str,
        help='input device (numeric ID or substring)')
    parser.add_argument(
        '-r', '--samplerate', type=int, help='sampling rate')
    args = parser.parse_args(remaining)

    if res == 'fr':
        models = 'model_fr'
    elif res == 'en':
        models = 'model_en'
    else:
        print('la langue entrée n\'est pas prise en contre par le système')
        models = None

    if models is not None:
        try:
            if args.model is None:
                args.model = models
            if not os.path.exists(args.model):
                print ("Please download a model for your language from https://alphacephei.com/vosk/models")
                print ("and unpack as {} in the current folder.".format(models))
                parser.exit(0)
            if args.samplerate is None:
                device_info = sd.query_devices(args.device, 'input')
                # soundfile expects an int, sounddevice provides a float:
                args.samplerate = int(device_info['default_samplerate'])

            model = vosk.Model(args.model)

            if args.filename:
                dump_fn = open(args.filename, "wb")
            else:
                dump_fn = None
            with sd.RawInputStream(samplerate=args.samplerate, blocksize = 8000, device=args.device, dtype='int16',
                                    channels=1, callback=callback):
                    print("Pour arreter l'enregistrement, Appuyer sur 'Ctrl+c' ")
                    
                    rec = vosk.KaldiRecognizer(model, args.samplerate)
                    capText = True
                    if res == 'fr':
                        print("Je suis à l'écoute ...")
                    elif res == 'en':
                        print('Im leasning ...')
                    while capText:
                        data = q.get()
                        if rec.AcceptWaveform(data):
                            result = json.loads(rec.Result())
                            if result['text'] != '':
                                capText = False
                                searchText = result['text']
                                print(searchText)
                                def index_phrase_fr():
                                    with open('fr.txt','r',encoding='utf-8') as f:
                                        tab = f.readlines()
                                        for text in tab:
                                            if searchText in text:
                                                read_text = text            
                                    index = tab.index(read_text)
                                    engine.setProperty("voice", voices[1].id)
                                    with open('en.txt','r',encoding='utf-8') as f:
                                        toto = f.readlines()[index:]
                                        for line in toto:
                                            titi = line 
                                            engine.say(titi)
                                            engine.runAndWait()
                                def index_phrase_en():
                                    with open('en.txt','r',encoding='utf-8') as f:
                                        tab = f.readlines()
                                        for text in tab:
                                            if searchText in text:
                                                read_text = text            
                                    index = tab.index(read_text)
                                    with open('fr.txt','r',encoding='utf-8') as f:
                                        toto = f.readlines()[index:]
                                        for line in toto:
                                            titi = line 
                                            engine.say(titi)
                                            engine.runAndWait() 
                                if res == 'fr':
                                    index_phrase_fr()    
                                elif res == 'en':  
                                    index_phrase_en()  
                            # else:
                                capText = True            
                        if dump_fn is not None:
                            dump_fn.write(data)

        except KeyboardInterrupt:
            print('\nDone')
            parser.exit(0)
        except Exception as e:
            parser.exit(type(e).__name__ + ': ' + str(e))
    else:
        print('Les langues prises en contre par le système sont : français et anglais')
    # ecouter_encor = input('voulez vous continier oui/non : ')
    # ecouter_encor = ecouter_encor.lower()
    # if ecouter_encor == 'oui'or ecouter_encor == 'o' or ecouter_encor == 'yes' or ecouter_encor == 'y':
    #     capText = ''
    #     capText = True
    # elif ecouter_encor == 'non'or ecouter_encor == 'n'or ecouter_encor == 'no' :
    #     parser.exit(0)

while True :
    run(answer)
