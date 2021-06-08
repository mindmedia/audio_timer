# audio_timer
Timer triggered by audio.

This is a python code that is run on raspberry pi. When some screams into a usb mic connected the raspberry pi, the code will check the rms value of the audio. When the rms is above a set value, the timer starts. Once the rms is lower a set value, the timer stops. And stays stopped until the reset button is pressed.
