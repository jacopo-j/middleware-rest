# Image Server Demo
![Python application](https://github.com/jacopo-j/middleware-rest/workflows/Python%20application/badge.svg)

Real life example of a scalable image server with OAuth authentication and AWS S3 storage.
## Features
- Self-documented *RESTful* API to manage users and their images ([link to Swagger interface](https://aqueous-castle-79099.herokuapp.com/swagger))
- Fully functional *OAuth2* Server
- Two ready-to-use OAuth2 *Clients*
- *Implicit*, *Password* and *AuthenticationCode* flows embedded into swagger
- Scalable image storage using *AWS S3* service to store and retrieve images
- Fully *navigable* API, following the Hypertext Application Language convention
- Automated build using Github Actions, with AWS S3 mocking

## Requirements
All the requirements are listed in _requirements.txt_, here a little explanation about them:
 - *Flask*, with two extensions:
    - *restx* to expose Swagger documentations through the code - the best doc is the code!
    - *SQLAlchemy* to manage databases through object-programming model
 - *Boto3*, to manage AWS S3 buckets
 - *Werkzeug*, for data structures managment and salt generation
 - *passlib*, for SHA256
 - *Authlib*, for RFC implementations of OAuth2 protocols
 - *moto*, to mock and test S3 buckets in CI/CD pipelines
 
## Usage
```
pip install -r requirements.txt 
python wsgy.py
```
### AWS S3
Images file are uploaded and saved into S3 buckets; therefore, follow the [doc](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html) to configure your credentials!
