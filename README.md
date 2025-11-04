# runpod-runner

Simple request runner for the runpod.io serverless api + automatic111 stable diffusion

## How to use

First you would need to setup build and deploy serverless worker on rupod.io, using https://github.com/runpod-workers/worker-a1111 repo.

You need to provide your secret in file called "secret" in the same directory as script.

For the first run you would need to provide your serverless worker endpoint with -p argument. It is cached for further usage

You can use your prompt to generate image. Example is provided in prompt_example.json.

You can use -h to check all the options available.


