def checkBattery():
	import digitalio, board
	from analogio import AnalogIn
	
	
	# define the bounds of your range
	#lower_bound = ...
	#upper_bound = ...

	# take the measurements
	measurements = [(AnalogIn(board.VOLTAGE_MONITOR).value * 3.3 / 65535) * 3 for _ in range(64)]

	# discard out of range measurements
	#measurements = [m for m in measurements if lower_bound <= m <= upper_bound]

	# calculate the average
	vsysVoltage = sum(measurements) / len(measurements)


	cutoff = {'alkaline':2.2, 'rechargeable':2.3, 'lithium':2.6, '':2.2}

	data = load_json()
	batteryType = data['battery_type']


	if vsysVoltage < cutoff[batteryType]:

		from playAudio import playAudio
		playAudio('lowBattery.mp3')
		with open('voltage.txt', 'a') as f:
			f.write(f'LOW BATTERY: {round(vsysVoltage, 2)}v\n')
		import alarm
		pin_alarm = alarm.pin.PinAlarm(pin=board.GP2, value=False, pull=True)
		alarm.exit_and_deep_sleep_until_alarms(pin_alarm)

	elif 3.6 < vsysVoltage < 4.4: #probably USB power with batts in, BAD!
		from playAudio import playAudio
		with open('voltage.txt', 'a') as f:
			f.write(f'POWER TROUBLE: {round(vsysVoltage, 2)}v\n')
		while True:
			playAudio('chime.mp3')
	elif vsysVoltage > 4: #on battery not USB
		pass
	else:
		try:
			with open('voltage.txt', 'r') as f:
				voltage_lines = [line for line in f]
		except:
			voltage_lines = []

		voltage_lines = voltage_lines[-99:] + [f'{round(vsysVoltage, 2)}v\n']  # Keep list to 100 entries

		# Now, open the file in write mode to overwrite it.
		with open('voltage.txt', 'w') as f:
			for line in voltage_lines:
				f.write(line)




	del board, digitalio, AnalogIn, vsysVoltage, cutoff

def load_json():
	import json
	try:
		with open("prompts.json", "r") as json_file:
			data = json.load(json_file)
		print('json loaded without incident')
	except:
		try:
			with open("prompts.json.bk", "r") as file:
				data = json.load(file)
			with open("prompts.json", "w") as file:
				json.dump(data, file)
			import os
			os.remove("prompts.json.bk")	
			print("error, loaded prompts.json.bk")
		except:
			try:
				with open("prompts_default.json", "r") as file:
					data = json.load(file)
				with open("prompts.json", "w") as file:
					json.dump(data, file)
				print("big error, loaded prompts_default.json")
			except:
				raise
	return data

def update_json(network_name=None, network_password=None, prompt=None, temperature=None, newSettings=[]):
	print('updating json...')
	import json
	from functions import load_json
	data = load_json()
	mode = data.get("current_mode")
	oldTopic = data['topic']
	for key, value in newSettings.items():
		if value:
			data[key] = value  # this will update the value of the key if it exists, or create a new key-value pair if it doesn't.

	# if prompt topic is different from before, clear out old messages
	if data['topic'] != oldTopic:
		last = data['prompts'][mode]['prompt'].pop()
		messages = data["prompts"][mode]["prompt"][:2]
		data['prompts'][mode]['prompt'] = data["prompts"][mode]["prompt"][:2]
		data['prompts'][mode]['prompt'].append(last)
		import os
		try:
			os.remove('clip.mp3')
		except:
			pass
	# If temperature is provided, the prompt list
	if temperature is not None:
		data["prompts"][mode]["temperature"] = float(temperature)		

	# If prompt is provided, the prompt list
	'''if prompt is not None:
		if mode:
			if "prompts" not in data:
				data["prompts"] = {}
			if mode not in data["prompts"]:
				data["prompts"][mode] = {}
			prompt_list = data["prompts"][mode].get("prompt", [])
			data['prompts'][mode]['prompt'].pop() #delete old prompt
			prompt_list.append({"content": prompt, "role": "user"})
			data["prompts"][mode]["prompt"] = prompt_list
	print('doing network stuff')'''
	# Parse the existing SSIDs and passwords
	wifi_list = data.get("networks", [])
	if network_name:
		# Add the new SSID and password to the list
		wifi_list.append((network_name, network_password))
		print("network info appended")
		data["networks"] = wifi_list
		with open("prompts.json.bk", "w") as file:
			json.dump(data, file)
		print('backup made')
	else:
		print('no network updates')

	# Save the updated content to the file
	with open("prompts.json", "w") as json_file:
		json.dump(data, json_file)
	print("json updated")

def join_wifi():
	import wifi
	import json
	from functions import load_json
	data = load_json()
	  
	# Parse the content to extract the SSIDs and passwords
	wifi_list = data.get("networks", [])
	del data
	for ssid, password in wifi_list:
		try:
			wifi.radio.connect(ssid, password)
			print('connected with IP:', wifi.radio.ipv4_address)
			del wifi_list
			return True
			
		except ConnectionError:
			print("Failed to connect to", ssid, password)
		except ValueError:
			print("Failed to connect to", ssid, password)
		except:
			raise
	#no wifi connection was made:
	print('no wifi network')
	return False
	
def htmlPage():
	with open('configPage.html', 'r') as file:
		htmlPage = file.read()
	return htmlPage