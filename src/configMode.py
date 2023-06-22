import gc
gc.collect()
print('free memory at start of configMode:', gc.mem_free()/1000,'kb')
from audiomp3 import MP3Decoder

#TODO: json correction
def load_prompt(): #for display on webpage
		gc.collect()
		from functions import load_json
		data = load_json()

		# Check the mode and load the corresponding prompt name
		mode = data.get("current_mode")

		if not mode:
			return "MODE ERROR"

		# Extract the desired value from the prompt key
		prompt_data = data.get("prompts", {}).get(mode, {}).get("prompt", [])
		del data
		gc.collect()
		if len(prompt_data) >= 3:
			return prompt_data[-1].get("content", "")

		return "PARSE ERROR"
print('free memory at configMode start:', gc.mem_free()/1000,'kb')
import socketpool
import wifi
from adafruit_httpserver.mime_type import MIMEType
from adafruit_httpserver.request import HTTPRequest
from adafruit_httpserver.response import HTTPResponse
from adafruit_httpserver.server import HTTPServer
from adafruit_httpserver.methods import HTTPMethod
import time
import microcontroller
import json
import board
import audiomixer
from audiopwmio import PWMAudioOut
audio = PWMAudioOut(board.GP1)
		
def url_decode(s): #good luck.
	result = []
	i = 0
	while i < len(s):
		c = s[i]
		if c == '+':
			result.append(' ')
		elif c == '%':
			hex_value = s[i+1:i+3]
			result.append(chr(int(hex_value, 16)))
			i += 2
		else:
			result.append(c)
		i += 1
	return ''.join(result)

def parse_raw_text(raw_text):
	print('raw text:', raw_text)
	key_value_pairs = raw_text.split('&')
	parsed_data = {}
	for key_value in key_value_pairs:
		key, value = key_value.split('=')
		parsed_data[key] = url_decode(value)
	return parsed_data
	
gc.collect()
print('free memory at configureWIFI start:', gc.mem_free()/1000,'kb')

mixer = audiomixer.Mixer(buffer_size=1024, voice_count=2, sample_rate=10000, channel_count=1, bits_per_sample=16, samples_signed=True)
audio.play(mixer)
print('playing audio')
while audio.playing:
	audio.stop() # stop the audio when wifi is setting up to prevent glitching noises
	print('setting up wifi')
	wifi.radio.stop_station()
	try:
		wifi.radio.start_ap('Positivity Pusher', 'positivity')
	except Exception as e:
		print('gotta reboot, in 5...')
		#########time.sleep(5)
		print('rebooting due to', e)
		microcontroller.reset()

	pool = socketpool.SocketPool(wifi.radio)
	server = HTTPServer(pool)

	@server.route("/", method=HTTPMethod.GET)
	def index(request: HTTPRequest):
		audio.stop()
		with HTTPResponse(request, content_type=MIMEType.TYPE_HTML) as response:
			from functions import htmlPage
			print('free memory after importing html:', gc.mem_free()/1000,'kb')
			from functions import load_json
			data = load_json()
			page = htmlPage()
			page = page.replace('{name}', data.get("name"))
			page = page.replace('{pronouns}', data.get("pronouns"))
			page = page.replace('{topic}', data.get("topic"))
			page = page.replace('{alkaline_checked}', 'checked' if data.get("battery_type") == 'Alkaline' else '')
			page = page.replace('{lithium_checked}', 'checked' if data.get("battery_type") == 'Lithium' else '')
			page = page.replace('{rechargeable_checked}', 'checked' if data.get("battery_type") == 'Rechargeable' else '')
			'''page = page.replace('{context_length}', str(data.get("context_length")))
			page = page.replace('{temperature}', str(data["prompts"][data["current_mode"]]["temperature"]))
			page = page.replace('{avoid}', str(data.get("avoid")))
			page = page.replace('{custom_prompt}', data["prompts"][data["current_mode"]]["prompt"][-1]["content"])'''
			num_prompts = len(data["prompts"][data["current_mode"]]["prompt"])
			recents = [message["content"] for message in data["prompts"][data["current_mode"]]["prompt"][2:num_prompts-2]][-3:] #select the messages after the first two, and before the last two (user message and upcoming unplayed message)
			for message in reversed(recents):
				page = page.replace("{recent-message}", message, 1)
			with open("loved_messages.json", 'r') as file:
				data = json.load(file)
			recentLoved = [message.split("(user reacted:")[0] for message in data["loved_messages"]]
			for message in reversed(recentLoved):
				page = page.replace("{favorite-message}", message, 1)
			page = page.replace("{recent-message}", "").replace("{favorite-message}", "") #so sloppy... removes placeholders not replaced earler.
			response.send(page)
			print('free memory after serving html:', gc.mem_free()/1000,'kb')

		gc.collect()
		mixer = audiomixer.Mixer(buffer_size=512, voice_count=1, sample_rate=10000, channel_count=1, bits_per_sample=16, samples_signed=True)
		audio.play(mixer) # play silence after serving the html page
		
	@server.route("/", method=HTTPMethod.POST)
	def buttonpress(request: HTTPRequest):
		audio.stop()
		gc.collect()
		print('free memory upon getting form:', gc.mem_free()/1000,'kb')

		raw_text = request.raw_request.decode("utf8")
		body_start = raw_text.find('\r\n\r\n') + len('\r\n\r\n')
		form_data_raw = raw_text[body_start:]
		parsed_data = parse_raw_text(form_data_raw)
		print(parsed_data)
		del raw_text, body_start, form_data_raw
		gc.collect()
		
		network_name = parsed_data.get("network_name")
		network_password = parsed_data.get("network_password")
		prompt = parsed_data.get("custom_prompt")
		temperature = parsed_data.get("temperature")
		newSettings = {"name":parsed_data.get("name"),
						"pronouns":parsed_data.get("pronouns"), 
						 "battery_type":parsed_data.get("battery_type"), 
						 "topic":parsed_data.get("topic"), 
						 "context_length":parsed_data.get("context_length"),
						 "avoid":parsed_data.get("avoid")}
		del parsed_data
		gc.collect()
		from functions import update_json
		print('free memory after updating json:', gc.mem_free()/1000,'kb')
		update_json(network_name, network_password, prompt, temperature, newSettings)
		del update_json
		
		with HTTPResponse(request, content_type=MIMEType.TYPE_HTML) as response:
			response.send("<html><head><style>body{font-family:Poppins,sans-serif;margin:0;background:linear-gradient(135deg,#f6d365,#fda085);display:flex;justify-content:center;align-items:center;height:100vh}h1{text-transform:uppercase;font-weight:700;font-size:calc(7vw+30px);color:#fff;margin-top:-20%}</style></head><body><h1>Confirmed!</h1></body></html>")
		print('free memory upon sending response:', gc.mem_free()/1000,'kb')
		gc.collect()
		
		clip = MP3Decoder(open("confirmed.mp3", "rb"))	
		clip.sample_rate = 10000			#slow down fast mp3s
		audio.play(clip)
		while audio.playing:
			pass
		print('done playing')
		microcontroller.reset()
		
	print('free memory before audio setup:', gc.mem_free()/1000,'kb')
	mixer.deinit()
	del mixer
	gc.collect()
	clip = MP3Decoder(open("setup.mp3", "rb"))	
	clip.sample_rate = 10000			#slow down fast mp3s
	audio.play(clip, loop=True)
	#server.serve_forever(str(wifi.radio.ipv4_address_ap))
	server.start(str(wifi.radio.ipv4_address_ap))
	print(f"Listening on {str(wifi.radio.ipv4_address_ap)}")
	import digitalio
	topButton = digitalio.DigitalInOut(board.GP2)
	topButton.direction = digitalio.Direction.INPUT
	topButton.pull = digitalio.Pull.UP
	startTime = time.monotonic()
	# serve the website for 5 minutes, after that, reboot
	while topButton.value and (time.monotonic() - startTime) < 300:
		server.poll()
	microcontroller.reset()