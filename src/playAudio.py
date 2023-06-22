def playAudio(clip):
	try:	
		print('loading audio stuff with', clip)
		import gc
		import time
		import board
		import digitalio
		led = digitalio.DigitalInOut(board.GP0)
		led.direction = digitalio.Direction.OUTPUT
		
		from audiomp3 import MP3Decoder
		theClip = MP3Decoder(clip)	 #set this up first for memory reasons?
		theClip2 = MP3Decoder(clip)	 #set this up first for memory reasons?
		theClip.sample_rate = 10000			  # this plays the audio slower because we request the tts at double speed 
		theClip2.sample_rate = 10000			  # this plays the audio slower because we request the tts at double speed 
		
		from audiopwmio import PWMAudioOut as AudioOut
		import audiomixer
		mixer = audiomixer.Mixer(buffer_size=1024, voice_count=2, sample_rate=10000, channel_count=1, bits_per_sample=16, samples_signed=True)
		audio = AudioOut(board.GP1)
		
		audio.play(mixer)
		mixer.voice[0].level = 1	
		mixer.voice[1].level = 1	
		mixer.voice[0].play(theClip)	
		mixer.voice[1].play(theClip2)

		print('playing clip!')
		while mixer.voice[0].playing:
			led.value = not led.value #blink the LED
			time.sleep(.15)
			
		led.value = True
		startTime = time.monotonic()
		topButton = digitalio.DigitalInOut(board.GP2)
		topButton.direction = digitalio.Direction.INPUT
		topButton.pull = digitalio.Pull.UP
		taps=0
		audio.stop()
		audio.play(mixer) #make a click to indicate end of playback
		if clip == 'clip.mp3':
			while audio.playing and (time.monotonic()-startTime < 5): #wait 5 seconds for user reactions
				if not topButton.value:
					taps += 1
					print('taps:', taps)
					startTime = time.monotonic() #extend the 5 second timer
					buttonStartTime = time.monotonic()
					while not topButton.value:
						if time.monotonic() - buttonStartTime > 1: #if the button is held down for more than 1 sec, replay the clip
							print('do the replay here')
							taps -= 1
							print('returning replay')
							topButton.deinit()
							led.deinit()
							audio.deinit()
							return("replay")
					try:
						del theClip, theClip2
					except:
						pass
					gc.collect()
					theChime = MP3Decoder('chime.mp3')	# credit ying16: https://freesound.org/people/ying16/sounds/353070/
					theChime.sample_rate = 10000		# match mixer sample rate 
					mixer.voice[0].play(theChime)	
					time.sleep(.1)
		
			
		
		audio.deinit()
		mixer.deinit()
		led.deinit()
		topButton.deinit()
		if clip == 'clip.mp3':
			import os
			os.remove('clip.mp3')
		del led
		del topButton
		del mixer
		try:
			del theClip
			del theClip2
			del theChime
		except:
			pass
		del MP3Decoder
		del audio
		return taps


	except Exception as e:  # Catch all exceptions
		try:
			led.deinit()
			del led
		except:
			pass
		try:
			audio.deinit()
			del audio
		except:
			pass
		
		if isinstance(e, OSError) and e.errno == 2 and 'clip.mp3' in str(e): # Check if the exception is a missing 'clip.mp3'
			pass  # Ignore the error, this just means a new clip must be loaded
		else:
			raise

