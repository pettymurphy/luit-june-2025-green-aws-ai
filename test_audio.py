from gtts import gTTS

text = "Welcome to Pixel Learning. This is a test file for multilingual audio conversion."
tts = gTTS(text, lang='en')
tts.save("test_audio_pixel_learning.mp3")
print("MP3 file created: test_audio_pixel_learning.mp3")
