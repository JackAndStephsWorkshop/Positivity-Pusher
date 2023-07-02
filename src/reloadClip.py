import gc
gc.collect()
print('now running reloadClip - free memory:', gc.mem_free()/1000,'kb')
import board
import digitalio
import alarm
import time
from playAudio import playAudio
pin_alarm = alarm.pin.PinAlarm(pin=board.GP2, value=False, pull=True)
led = digitalio.DigitalInOut(board.GP0)
led.direction = digitalio.Direction.OUTPUT
led.value = True #loading light on

try:
	try: #check to see if we have a clip, and it is big enough to be a complete mp3
		import os
		x=os.stat('clip.mp3')
		if x[6] > 1000:
			print('clip found, size:', x[6]/1000, 'kb')
			for x in range(4):
				led.value = not led.value
				time.sleep(.1)
			led.deinit()
			del led
			playAudio('chime.mp3')
			print('clip found')
			alarm.exit_and_deep_sleep_until_alarms(pin_alarm)

		else:
			raise Exception("MP3 file issue")
			playAudio('sorry.mp3') #todo- new message for here?
			
	except Exception as e: #No clip or clip too small, need to load one up!
		print('problem:', e)				
		gc.collect()
		import ssl
		import socketpool
		import wifi
		import adafruit_requests
		from random import randint
		import os
		import time
		from functions import join_wifi
		import json
	
		print('loaded libs - free memory:', gc.mem_free()/1000,'kb')

		def getText():
			print('Getting text. Memory before loading request json:', gc.mem_free()/1000,'kb')
			from functions import load_json
			tries = 0
			troubleString=False
			success = False
			while tries < 5 and success == False:
				data = load_json()
				mode = data['current_mode']
				theBundle = dict(data['prompts'][mode])

				#theBundle = data['prompts'][mode]
				gc.collect()
				print('memory after json loaded:', gc.mem_free()/1000,'kb')
				reminder=''
				name = data['name']
				pronouns = data['pronouns']
				topic = data['topic']
				
				if troubleString:
					reminder += "(Note to assistant: Remember to start and stop with quotation marks:\"\".\nGeneric Example:\n\"You're doing a great job, <name>!\"\n) "
					print('TROUBLESTRING ADDRESSED')
			
				if (data['push_count'] + 1) % 3 == 0:
					reminder +="(Note to assistant: Look over all the prior messages in our conversation. Choose a distinctly different modality and vocabulary for this next message) "
					print('SHAKEUP')
				
				theBundle["prompt"][-1]['content'] = reminder + theBundle["prompt"][-1]['content']
			
				if (data['push_count']) % 7 == 0:
					new_prompt = {"content": "(Note to assistant: Remember to start and stop with quotation marks:\"\". Please use proper grammer and don't use emoji. Avoid cliché!\nGeneric Example:\nYou're doing a great job, <name>!\nBe nonviolent! NEVER use violent language. Phrases like \"you are a warrior\", \"fight your battle\", \"combat those thoughts\", \"conquer your fear\", \"victory over opposition\", etc are examples of inappropriate violent language.)", "role": "user"}
					theBundle['prompt'].insert(-1, new_prompt) #insert at end
					print(' REMINDER')
			
				if (data['push_count'] + 1) % 5 == 0:
					new_prompt = {"content": "(Note to assistant: Please make sure all subsequent messages are coherent and concise.)", "role": "user"}
					theBundle['prompt'].insert(-1, new_prompt) #insert at end
					print('COHERENCE REMINDER')

				if (data['push_count'] + 1) % 4 == 0: #insert a loved message
					with open("loved_messages.json", 'r') as file:
						lovedData = json.load(file)
						if lovedData['loved_messages']:
							from random import choice
							message = choice(lovedData['loved_messages'])
							new_prompt = {"content": f"{message}", "role": "user"}
							theBundle['prompt'].insert(-1, new_prompt) #insert random loved message
						else:
							print("No loved messages found.")
				del data
				gc.collect()
				
				badass=37289
				battle=38471
				space_battle=3344
				#hyphen=12
				space_hyphen=532
				hyphen_comma=20995
				en_dash=1906
				em_dash=960
				space_en_dash= 784
				space_em_dash= 532
				fighter=24733
				space_fighter=10543
				fight=15481
				space_fight=1907
				fighting=26594
				space_fighting=4330
				killing=5170
				kill=1494
				astrisk=9
				doubleAstrisk=1174
				tripleAstrisk=8162
				doubleDollar=13702
				amazing=4998
				lucky=9670
				crushing=24949
				slaying=45183
				god=25344
				space_god=5770
				God=13482
				space_God=1793
				space_bless=12012
				space_blessing=20027
				space_warrior=16491	# note: actually ' warrior'
				biases = {fighter:-100, space_fighter:-100, en_dash:-100, space_en_dash:-100, em_dash:-100, space_em_dash:-100, space_fighting:-100, space_fight:-100, space_bless:-100, space_blessing:-100, god:-100, space_god:-100, space_God:-100, God:-100, battle:-100, space_battle:-100, space_hyphen:-100, hyphen_comma:-100, fight:-100, slaying:-100, crushing:-50, lucky:-1, amazing:-1, badass:-100,  killing:-100, kill:-100, astrisk:-100, doubleAstrisk:-100, doubleDollar:-100}

				# replace template holders
				theBundle["prompt"][-1]['content'] = theBundle["prompt"][-1]['content'].replace('<name>', name).replace('<pronouns>', pronouns).replace('<topic>', topic)
				# make the actual request to openai
				pool = socketpool.SocketPool(wifi.radio)
				requests = adafruit_requests.Session(pool, ssl.create_default_context())
				url = "https://api.openai.com/v1/chat/completions"
				headers = {"Content-Type": "application/json",
							"Authorization": os.getenv('OPEN_AI_KEY')}
				jsonData = {"model": theBundle["model"],
						"temperature": theBundle["temperature"],
						"max_tokens": theBundle["tokens"],
						"messages": theBundle["prompt"],
						"frequency_penalty":1,
						"presence_penalty":1,
						"logit_bias": biases}
				print("\n\nprompt to send:\n", theBundle["prompt"])
				del theBundle
				gc.collect()				
				startTime = time.monotonic()
				try:
					response = requests.request("POST", url, json=jsonData, headers=headers, timeout=15)
					print('response status code=', response.status_code )
					if response.status_code == 400: #this prompt is failing, so revert to the backup 
						print('AI FAIL:', response.text)
						os.remove("prompts.json")
						raise Exception("AI status 400, prompts.json removed")
			
					response = json.loads(response.text)
					completion_tokens = response['usage']['completion_tokens']
					role = str(response['choices'][0]['message']['role'])
					response = str(response['choices'][0]['message']['content'])
					response = response.replace("-,", ",")       # convert hyphens to commas. MS TTS doesn't handle hyphens well
					response = response.replace(" -", ",")       # convert hyphens to commas. MS TTS doesn't handle hyphens well
					response = response.replace("- ", ", ")        # convert hyphens to commas. MS TTS doesn't handle hyphens well
					response = response.replace(" – ", ", ")       # convert en dashes to commas. MS TTS doesn't handle en dashes well
					response = response.replace("– ", ", ")        # convert en dashes to commas. MS TTS doesn't handle en dashes well
					response = response.replace(" — ", ", ")       # convert em dashes to commas. MS TTS doesn't handle em dashes well
					response = response.replace("— ", ", ")        # convert em dashes to commas. MS TTS doesn't handle em dashes well
					response = response.replace("kinder", "kynder")# pronounce the word "kinder" as in "be kinder" and not like a german
					#print('full response:', response)
					try:
						#take only what is between quotes (including the quotes)
						start = response.find('"')  	# The start index of the first occurrence of " plus 1
						end = response.rfind('"') + 1  	# The end index of the last occurrence of "
						if start != end - 1:  # if not pointing at the same quote
							response = response[start:end]  # Slicing the string from start to end
							success = True
						else:
							print('\n\nTROUBLE STRING:\n\n', response, "\n\n")
							troubleString=True
					except:
						troubleString=True
				except Exception as e:
					print('request failed:', e)
					#print(response)
					tries += 1
			if success:
				del jsonData
				gc.collect()
				print('time to complete:', time.monotonic() - startTime)
				print('free memory:', gc.mem_free()/1000,'kb.')
				print('updating prompt')
				gc.collect()
				contextLength = 10
				data = load_json()

				user_prompt = data['prompts'][mode]['prompt'].pop() #remove and save the last message
				system_prompts = data['prompts'][mode]['prompt'][:2]		#save the system and first assistant prompt
				data['prompts'][mode]['prompt'] = data['prompts'][mode]['prompt'][2:]#remove the system and first assistant prompt
				data['prompts'][mode]['prompt'].append({"role": role, "content": response}) #append new response
				print('new prompts after appending latest response:', data['prompts'][mode]['prompt'])
				if len(data['prompts'][mode]['prompt']) > contextLength:
					print('pruning prompt list')
					data['prompts'][mode]['prompt'] = data['prompts'][mode]['prompt'][-contextLength:]
				data['prompts'][mode]['prompt'] = system_prompts + data['prompts'][mode]['prompt'] # insert system prompts at the beginning of the list

				data['push_count'] += 1
			
				#remove old reminders:
				try:
					start_marker = "(Note to assistant:"
					end_marker = ")"

					start_index = user_prompt["content"].find(start_marker)
					end_index = user_prompt["content"].find(end_marker, start_index + len(start_marker))

					if start_index != -1 and end_index != -1:
						user_prompt["content"] = user_prompt["content"][:start_index] + user_prompt["content"][end_index + len(end_marker):]
						print('old reminders removed')
				except:
					print('no old reminders found')	
				
				user_prompt["content"] = user_prompt["content"].strip()
				
				#add new reminders. todo: improve this functionality by saving token length of response, so length can be addressed before sending
				reminder=''
				if completion_tokens > 75:
					reminder += "(Note to assistant: These are getting a bit long. Please make this next affirmation shorter than the previous examples.) " 
				user_prompt["content"] = user_prompt["content"] + reminder
				data['prompts'][mode]['prompt'].append(user_prompt)
				with open("prompts.json", "w") as file:
					json.dump(data, file)
				del data
				del requests
				gc.collect()
				print('free memory after cleaning up:', gc.mem_free()/1000,'kb.')
				return(response)
			else:
				raise Exception("OpenAI issue")

		def getSpeech(words):
			try:
				os.remove('clip.mp3')
			except:
				pass
			gc.collect()
			print('free memory:', gc.mem_free()/1000,'kb. Getting speech...')
			startTime = time.monotonic()
			pool = socketpool.SocketPool(wifi.radio)
			requests = adafruit_requests.Session(pool, ssl.create_default_context())
		
			#https://learn.microsoft.com/en-us/azure/cognitive-services/speech-service/speech-synthesis-markup-voice
			#https://learn.microsoft.com/en-us/azure/cognitive-services/speech-service/language-support?tabs=tts#voice-styles-and-roles
			#theStyle = choice(['cheerful', 'friendly', 'excited', 'shouting', 'whispering', 'hopeful'])
			#theVoice = choice(['Aria', 'Davis', 'Guy', 'Jane', 'Jason', 'Jenny', 'Nancy', 'Sara', 'Tony'])
			theSpeechPT1=(f"<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xmlns:mstts='https://www.w3.org/2001/mstts' xml:lang='en-US'><voice xml:lang='en-US' name='en-US-AriaNeural' effect='eq_car'><mstts:express-as style='whispering' styledegree='.75'><prosody volume='+20.00%' rate='+{randint(70,90)}%' pitch='+100%'>")
			theSpeechPT2=("</prosody></mstts:express-as></voice></speak>")
			startTime = time.monotonic()
			url = 'https://westus.tts.speech.microsoft.com/cognitiveservices/v1'
			payload = theSpeechPT1 + words + theSpeechPT2
			headers = {'Ocp-Apim-Subscription-Key': os.getenv("AZURE_TTS_KEY"),
					'X-Microsoft-OutputFormat': 'audio-16khz-32kbitrate-mono-mp3',
					'Content-Type': 'application/ssml+xml'}
			success = False
			tries = 0
			while tries < 3 and success == False:
				try:
					response = requests.request("POST", url, data=payload, headers=headers)
					success = True
					#print('speech request complete on attempt', tries+1)
				except:
					print('request ', tries+1, ' failed')
					tries += 1
					time.sleep(1)
					
			del theSpeechPT1, theSpeechPT2, url, words, headers
			gc.collect()
			if response.status_code == 200: #good mp3, save it to disk
				startTime = time.monotonic()
				with open('clip.mp3', 'wb') as f:
					for chunk in response.iter_content(chunk_size=4096):
						f.write(chunk)
				del response
				gc.collect()
				x=os.stat('clip.mp3')
				print('mp3 size:', x[6]/1000, 'kb')
				if x[6] < 1000:
					print('mp3 file too small. trying again, delete it then reboot.')
					os.remove('clip.mp3')
					raise Exception("pusher: bad mp3 size!")
				print('time to save mp3:', time.monotonic() - startTime)

				fs_stat = os.statvfs('/')
				total_space_kb = fs_stat[0] * fs_stat[2] / 1024
				free_space_kb = fs_stat[0] * fs_stat[3] / 1024
				used_space_kb = total_space_kb - free_space_kb
				percent_full = (used_space_kb / total_space_kb) * 100
				print('free ram:', gc.mem_free()/1000,'kb')
				print("Free space on FS:", free_space_kb, 'KB')
				print("Percentage of FS full:", int(percent_full))
				return True
			else:
				print('bad tts status')
				#raise Exception(f"bad status code on TTS response: {response.status_code}\nthe string was: {payload}")
		
		wifiResult = join_wifi()
		gc.collect()
		if not wifiResult:
			led.deinit()
			del led
			raise Exception('-no wifi')
		print('joined wifi- free memory:', gc.mem_free()/1000,'kb')
		success=False
		loops=0
		try:
			led.deinit()
			del led
		except:
			pass
		from functions import checkBattery
		checkBattery()
		del checkBattery
		led = digitalio.DigitalInOut(board.GP0)
		led.direction = digitalio.Direction.OUTPUT
		led.value = True
		while not success and loops < 2:	#three tries to load the mp3 
			words = getText() #load the text
			print('the words:', words)
			success = getSpeech(words) #load the audio
			gc.collect()
			if success:
				with open("prompts.json", "r") as file:
					data = json.load(file)
				with open("prompts.json.bk", "w") as file:
					json.dump(data, file)
				print('backup created')
				del data
				gc.collect
				for i in range(10):
					led.value = not led.value
					time.sleep(.1)
				from functions import updateCheck
				updateCheck()
				led.deinit()
				del led
				playAudio('chime.mp3')
				print('rebooting')
				break
			else:
				print('TRYING AGAIN')
				loops+=1
		if not success:
			raise Exception('tried three times, couldnt get mp3')

except Exception as e:
	print(e)
	if str(e) == "-no wifi":
		try:
			led.deinit()
			del led
		except:
			pass
		playAudio('wifiFail.mp3')
	elif str(e) == "[Errno 30] Read-only filesystem":
		try:
			led.deinit()
			del led
		except:
			pass
		playAudio('file.mp3')
	else:
		import traceback
		print('-reloadClip main try block, exception:', str(traceback.format_exception(e)))
		try:
			with open('crash.txt', 'a') as f:
				import traceback
				f.write('\nreloadClip crash:' + ''.join(traceback.format_exception(e)))
		except:
			pass
		try:
			led.value=True
		except:
			led = digitalio.DigitalInOut(board.GP0)
			led.direction = digitalio.Direction.OUTPUT
		for i in range(10):
				led.value = not led.value
				time.sleep(.1)
		led.deinit()
		del led
		playAudio('sorry.mp3')

# at last, always:
alarm.exit_and_deep_sleep_until_alarms(pin_alarm)