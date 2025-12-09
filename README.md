# AllPets - Pet Care AI Assistant
AllPets is a web application that classifies images of a wide variety of pets and provides general care guidance. This combination of image classification and text generation within a chatbot interface creates a unified pet care assistant that decreases reliance on biased pet care employees and provides a convenient resource for new pet parents.

# What it Does
AllPets allows users to upload a photo of a pet and receive a pet prediction using zero-shot classification with a CLIP model, identifying the species from a set of common pets. Once identified, the app uses an instruction fine-tuned Phi-1.5 model to generate care information, including feeding advice, habitat/enclosure requirements, and stimulation/outdoor time recommendations. AllPets can also answer general pet care related questions without including an image to classify. The system integrates a React frontend with a FastAPI backend, serving both image classification and natural-language generation through adaptable API endpoints, complete with extensive logging and error handling. Thus, AllPets is a helpful, accessible assistant for new pet owners seeking quick, comprehensive pet care guidance.

# Quick Start
This web app is functional and has been deployed using AWS. You can access the application with the following link:
http://ec2-18-224-202-87.us-east-2.compute.amazonaws.com:8000/

The ML models used in this web app may take up to a minute to generate text responses and classify images. Please allow the models enough time to complete inference!

# Video Links
[Project Demo](videos/project_demo.mp4)

[Technical Walkthrough](videos/tech_walkthrough.mp4)

# Evaluation
Full Prompt Engineering Comparison Table

![Prompt Engineering Full Evaluation](images/prompts_full.png "Prompts Full")

Inference times are reported in the above table under the column name "time_s".

Simplified Prompt Engineering Comparison Table - prompts and responses only

![Prompt Engineering Evaluation](images/prompts.jpg "Prompts")

While all of the responses took about the same amount of time to generate (an example of measuring inference time), two prompts stood out with the most keyword matches - prompts 0 and 2. Keyword matches indicate whether the responses were able to pinpoint specific care topics I am looking for, such as food and exercise. I chose these keywords as they indicate important details for understanding pet care. Although prompt 2 did fulfill the maximum keyword matches, it also added extra questions at the end, such as "What should be included on an animal's diet plan?" Prompt 1 begins generating math-related questions, whereas prompt 3 lists rabbit breeds unnecessarily. Overall, prompt 0 provides a much more holistic, comprehensive review of rabbit care that is more helpful than any of the other prompts provided, specifying topics like "feeding" and "enclosure." This also makes sense because prompt 0 takes advantage of the prompt format I used to instruction fine-tune my model, which involved Context:, Question:, and Answer: sections. I ended up using prompt 0 to generate care summaries for pets classified via image upload.

- This information is pulled from my [eval.ipynb](notebooks/eval.ipynb)

# Individual Contributions
This was a solo project.