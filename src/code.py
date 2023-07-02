try:	
	import alarm
	from playAudio import playAudio
	if alarm.wake_alarm:
		import gc
		finished=False
		
		while not finished:
			#gc.collect()
			result = playAudio('clip.mp3')
			print('play result:', result)
			gc.collect()
			if result == 'replay':
				print('replay request!')
				finished=False
			elif result == 0:
				print('played clip once, no loves, no repeat')
				finished=True
			elif result == None:
				print('playAudio didnt return anything')
				finished=True
			else:	#we played a clip and got a rating
				finished=True
				from functions import load_json
				data = load_json()
				last_entry = data["prompts"][data["current_mode"]]["prompt"][-2]["content"]
				#last_entry += ' (user reacted:' + '\u2764\uFE0F' * result + ')' #add the number of loves as emoji hearts
				del data
				gc.collect()
				with open("loved_messages.json", "r") as file:
					import json
					data = json.load(file)
					data["loved_messages"].append(last_entry)
					if len(data["loved_messages"]) > 20:
						data["loved_messages"].pop(0) 
				with open("loved_messages.json", "w") as file:
					json.dump(data, file)
				del data
				gc.collect()
			
	else:
		import microcontroller
		if microcontroller.cpu.reset_reason == microcontroller.ResetReason.RESET_PIN:
			import supervisor
			supervisor.set_next_code_file('configMode.py')
			supervisor.reload()
		
		elif microcontroller.cpu.reset_reason == microcontroller.ResetReason.POWER_ON or microcontroller.ResetReason.SOFTWARE:
			try:
				with open("test.txt", "w") as file:
					file.write('test')
				playAudio('powerOn.mp3')
				
			except:
				playAudio('file.mp3')
				while True:
					pass
			

except Exception as e:
	print(e)
	if str(e) == "-no wifi":
		pass
	else:
		import time
		print('CRASH!')
		with open('crash.txt', 'a') as f:
			import traceback
			f.write('\n-' + ''.join(traceback.format_exception(e)))
		from playAudio import playAudio
		playAudio('sorry.mp3')
	
import supervisor
supervisor.set_next_code_file('reloadClip.py')
supervisor.reload()