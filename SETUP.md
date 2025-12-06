# Setup Directions

This web app is functional and has been deployed using AWS. You can access the application with the following link:
http://ec2-18-224-202-87.us-east-2.compute.amazonaws.com:8000/

# Hosting Locally

If you would like to host this web app locally on your computer:

1. Install UI dependencies and build app
```bash
# run from ui/ directory
npm install
npm run build
```
2. Install API dependencies
```bash
# run from api/ directory
pip install -r requirements.txt
```
3. Start the API
```bash
# run from api/ directory
uvicorn main:app --reload
```
4. Test your setup - navigate to `localhost:8000/`