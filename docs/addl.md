# Additional Information

This web app was deployed using AWS EC2. I initially ran out of storage while loading my models in, so I attached a volume to my virtual machine, where I store the base Phi-1.5 model.

## Design Choices
- When running inference on my text generation model (instruction fine-tuned Phi-1.5), a design choice I made was to use parameters repetition_penalty=1.2 and no_repeat_ngram_size=3. These are parameters added to reduce repetition in responses.

- My web app demonstrates a multi-stage ML pipeline, because once an image is uploaded, CLIP classifies it, and this output is then sent into my text generation model to produce a care summary about the predicted pet.

- I chose to make my web app into a very minimal, chatbot-style application to provide familiarity to users who've interacted with similar AI assistant services on other websites.

- I chose to use a tech stack with React frontend and FastAPI backend in order to create a simple, minimal frontend while running the model on the backend. In this way, model inference time would not be variable based on the client's computer.