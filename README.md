# Image Server Demo
![Python application](https://github.com/jacopo-j/middleware-rest/workflows/Python%20application/badge.svg)
Real life example of a scalable image server with OAuth authentication.
## Features
- Self-documented *RESTful* API to manage users and their images
- Fully functional *OAuth2* Server
- Two ready-to-use OAuth2 *Clients*
- *Implicit*, *Password* and *AuthenticationCode* flows embedded into swagger
- Scalable image storage using *AWS S3* service to store and retrieve images
- Fully *navigable* API, following the Hypertext Application Language convention

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

## AWS S3
Images file are uploaded and saved into S3 buckets; therefore, setup of the ENV Variables is needed!
