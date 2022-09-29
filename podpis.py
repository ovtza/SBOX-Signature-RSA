import os
import hashlib
import PySimpleGUI as gui
from Cryptodome.PublicKey import RSA
from Cryptodome.Cipher import PKCS1_OAEP
from scipy.io.wavfile import write
import sounddevice as REC
import sboxtrng
import numpy as np

print("Nagrywanie...")
AUDIO_LENGTH_SECONDS = 60 # Czas trwania nagrania
#Czestotliwosc probkowania = 44100, Kanał = MONO
rec = REC.rec( int(AUDIO_LENGTH_SECONDS * 44100), samplerate = 44100, channels = 1, dtype=np.int16)
REC.wait()
print("Nagrano...")
write('temp-audio.wav', 44100, rec)
print("Zapisano audio")

#W zmiennej trng zwracany jest ciag liczb prawdziwie losowych z generatora sboxtrng
trng = sboxtrng.trngVector('temp-audio.wav')

#funkcja zapisująca próbki z generatora
def sboxtrngGen():
    with open('soundsamples.txt', 'wb') as f:
        np.save(f, trng)

#wygenerwowanie pliku z probkami z sbox trng
sboxtrngGen()
#utworzenie klucza z probek sbox trng
with open('soundsamples.txt', 'rb') as f:
    key = RSA.generate(1024, f.read)

#Utworzenie gui
gui.theme('DarkAmber')
font = ("Arial", 16)
guiLayout = [[gui.Text('Wpisz wiadomość do zaszyfrowania', font=font)],
             [gui.InputText(), gui.Submit('Ok')]]
window = gui.Window('Wykonaj akcje', guiLayout)
event, values = window.read()
window.close()

wiadomosc = values[0]
hash = hashlib.sha224(wiadomosc.encode('ascii')).hexdigest()
#utworzenie szyfru
cipher = PKCS1_OAEP.new(key.public_key())
#zaszyfrowanie wiadomosci
zaszyfrowana_wiadmosc = cipher.encrypt(hash.encode('ascii'))

guiLayout = [[gui.Text('Wygenerowano klucz prywatny', font=font)],
            [gui.Text('Edycja: '), gui.InputText(key.export_key().decode('ascii'), size=(40, 10), ) ],  # Możliwość edycji klucza prywatnego
            [gui.Submit('Ok')]]

window = gui.Window('Edytuj lub pozostaw niezmienony klucz', guiLayout)

event, values = window.read()
window.close()

text_input_private_key = values[0]  # Zczytanie edytowanego klucza do zmiennej

if text_input_private_key != key.export_key().decode('ascii'):  # Porównanie klucza prywatnego z edytowanym i wyświetlenie odpowiednich wiadomości
    guiLayout = [[gui.Text('Klucz prywatny zmienił się!!', font=font)],
                    [gui.Text('Klucz nr 1'), gui.Text(text_input_private_key)],
                    [gui.Text('Klucz nr 2'), gui.Text(key.export_key().decode('ascii'))],
                    [gui.Submit('Ok')]]

    window = gui.Window('Porownanie kluczy dla wiadomosci', guiLayout)
    event, values = window.read()
    window.close()
else:
    guiLayout = [[gui.Text('Klucz prywatny nie zmienił się', font=font)],
                    [gui.Text('Klucz nr 1'), gui.Text(text_input_private_key)],
                    [gui.Text('Klucz nr 2'), gui.Text(key.export_key().decode('ascii'))],
                    [gui.Submit('Ok')]]

    window = gui.Window('Porownanie kluczy dla wiadomosci', guiLayout)
    event, values = window.read()
    window.close()
    
    guiLayout = [[gui.Text('Edytuj wiadomość')],
              [gui.InputText(wiadomosc)],  # Możliwość edycji wiadomosci
              [gui.Submit('Ok')]]

    window = gui.Window('Okienko', guiLayout)

    event, values = window.read()
    window.close()
    edited_message = values[0]

    decryptor = PKCS1_OAEP.new(key)  # Stworzenie dekryptora
    decrypted_message = decryptor.decrypt(zaszyfrowana_wiadmosc)  # Dekrypcja wiadomośći
    if decrypted_message == hashlib.sha224(edited_message.encode('ascii')).hexdigest().encode('ascii'):
        guiLayout = [[gui.Text('Klucze SHA są identyczne. Treść wiadomości nie została zmieniona')],
                    [gui.Text('Wiadomosc NR1 ='), gui.Text(decrypted_message)],
                    [gui.Text('Wiadomosc NR2 ='), gui.Text(hashlib.sha224(edited_message.encode('ascii')).hexdigest().encode('ascii'))],
                    [gui.Submit('Ok')]]

        window = gui.Window('Porownanie SHA dla wiadomosci', guiLayout)
    else:
        guiLayout = [[gui.Text('Klucze SHA są różne. Treść wiadomości została zmieniona!')],
                    [gui.Text('Wiadomosc NR1 ='), gui.Text(decrypted_message)],
                    [gui.Text('Wiadomosc NR2 ='), gui.Text(hashlib.sha224(edited_message.encode('ascii')).hexdigest().encode('ascii'))],
                    [gui.Submit('Ok')]]

        window = gui.Window('Porownanie SHA dla wiadomosci', guiLayout)
    
    event, values = window.read()
    window.close()
    print("")
    print("Wiadomosc NR1 = ", decrypted_message)
    print("Wiadomosc NR2 = ", hashlib.sha224(edited_message.encode('ascii')).hexdigest().encode('ascii'))
#usuniecie pliku z probkami
os.remove('soundsamples.txt')
#usuniecie pluku audio
os.remove('temp-audio.wav')