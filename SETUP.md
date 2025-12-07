# Setup Directions

This web app is functional and has been deployed using AWS. You can access the application with the following link:
http://ec2-18-224-202-87.us-east-2.compute.amazonaws.com:8000/

The ML models used as a part of this web app may take up to a minute to generate text responses and classify images. Please allow the models enough time to complete inference!

# Hosting Locally

If you would like to host this web app locally on your computer:

1. Install UI dependencies and build front-end
```bash
cd ui
npm install
npm run build
cd ..
```
2. Install API dependencies
```bash
cd api
pip install -r requirements.txt
```
3. Start the back-end
```bash
uvicorn main:app --reload
```
4. Test your setup at `localhost:8000/`