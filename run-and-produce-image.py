import json
import base64
import runpod
import argparse
import os
import copy
import humanize
from datetime import datetime

#TODO: get costs from actual endpoint if possible. Put your costs here
costPerSecond = 0.00019

#Initialazing argparser
parser = argparse.ArgumentParser(description="Run and runpod ip for automatic with stable diffusion and output images and raw responses into files")
parser.add_argument("prompt", help="Path to the JSON file containing the prompt that will be passed to runpod")
parser.add_argument("-d", "--dry_run", action="store_true", help="Without this it will be only dryrun, without making actual request")
parser.add_argument("-o", "--output", default="output", help="Directory where we are putting outputs")
parser.add_argument("-r", "--raw_output", default="raw_responses", help="Directory where we are storing raw json responses")
parser.add_argument("-t", "--test", action="store_true", help="Test with mock response in response_example.json")
parser.add_argument("-e", "--debug_raw", action="store_true", help="Do we need to write raw response for debug purposes?")
parser.add_argument("-q", "--queue_size", type=int, default=1, help="Queue multiple requests simultaniously, using more then one serverless worker.")
parser.add_argument("-p", "--endpoint", help="Endpoint of your serverless api on runpod.io")
args = parser.parse_args()

#Loading secret
if os.path.exists("secret"):
    with open("secret", "r") as secret_file:
        runpod.api_key = secret_file.read().strip()
else:
    print("Please put your secret in file named secret near the script. Remember not to put it anywhere public!")
    exit()

#Loading endpoint
cache_filename = "cache.json"
endpoint = str(args.endpoint or "")
if endpoint == "":
    #Attempt to get cached endpoint
    if os.path.exists(cache_filename):
        with open(cache_filename, "r") as cache_file:
            cache_data = json.load(cache_file)
            endpoint = cache_data["endpoint"]
else:
    #Cache settings for future use
    cache_data = {}
    cache_data["endpoint"] = endpoint
    with open(cache_filename, "w") as cache_file:
        json.dump(cache_data, cache_file, indent=4)

if endpoint == "":
    print("Not able to locate endpoint, please specify it with -p in arguments")
    exit()

#Loading prompt
with open(args.prompt) as prompt_file:
    prompt = json.load(prompt_file)

print("Prompt to be used:")
print(prompt)

#Forecast of output size - there is limit of 20 MB for all runpod post calls
limit = 20 * 1024 * 1024
estimatePngPerByte = 1.5
base64Overhead = 1.33
width = prompt["input"]["width"]
height = prompt["input"]["height"]
batch_size = prompt["input"].get("batch_size", 1)
estimateSize = batch_size * width * height * estimatePngPerByte * base64Overhead
print(f"Estimate output size: {humanize.naturalsize(estimateSize)}")
if estimateSize > limit:
    print(f"Job fill fail, expected output is more then 20MB, exiting...")
    exit()

#Actual request to the runpod api
run_requests = []
responseOutputs = []

if args.test:
    print("Using mock response from repository to test image creation and stuff")
    with open("response_example.json", "r") as response_example:
        response = json.load(response_example)
        responseOutputs.append(response)
elif not args.dry_run:
    endpoint = runpod.Endpoint(endpoint)    

    for i in range(args.queue_size):
        run_requests.append(endpoint.run(prompt))

    print(f"Running {args.queue_size} async requests...")

    approximateCost = 0
    for run_request in run_requests:
        responseOutputs.append(run_request.output(timeout=600))
        executionTime = run_request._fetch_job()["executionTime"]
        approximateCost += costPerSecond * executionTime / 1000
    
    print(f"Job complete! You've just spent approximately {approximateCost:.4f}$")    
else:
    print("Dry run. Skipping actual request. Everything else seems to be in order.")
    exit()

#Processing responses
base_filename = datetime.now().strftime("%Y%m%d_%H%M%S")

images = []
try:
    for responseOutput in responseOutputs:
        images = images + responseOutput["images"]

    print(len(images), "images are in responses!")
except Exception as e:
    print("Cannot get images, probably output more than 20 MB, exiting...")
    exit()

response_filename = f"{args.raw_output}/{base_filename}.json"
counter_json = 1
for responseOutput in responseOutputs:
    while os.path.exists(response_filename):
        response_filename = f"{args.raw_output}/{base_filename}_{counter_json}.json"
        counter_json += 1

    os.makedirs(args.raw_output, exist_ok=True)

    with open(response_filename, "w") as response_file:
        if not args.debug_raw:
            del responseOutput["images"]
        json.dump(responseOutput, response_file, indent=4)

os.makedirs(args.output, exist_ok=True)

counter_png = 1
out_image_filename = f"{args.output}/{base_filename}.png"
for image in images:
    image_bytes = base64.b64decode(image)
    
    while os.path.exists(out_image_filename):
        out_image_filename = f"{args.output}/{base_filename}_{counter_png}.png"
        counter_png += 1

    with open(out_image_filename, "wb") as out_image_file:
        out_image_file.write(image_bytes)
        
print("All seems to be sucessfull! Enjoy your art ;)")