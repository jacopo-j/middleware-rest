# Image Server Demo
Real life example of a scalable image server with OAuth authentication, featuring:
- Self-documented *RESTful* API to manage users and their images
- Fully functional *OAuth2* Server
- Two ready-to-use OAuth2 *Clients*
- *Implicit*, *Password* and *AuthenticationCode* flows embedded into swagger
- Scalable image storage using *AWS S3* service to store and retrieve images
- Fully *navigable* API, following the Hypertext Application Language convention

# Explore
You can start your journey by registering an account, using `/register` in the `api` Namespace.
Now, you may want to click `Authorize` to get the *really* important OAuth authentication! You can set up your own client using `/create_client` in the auth Namespace, but we were kind enough to register already two Clients, with the following client_id (client_secrets are `secret`, don't do this in production!):
- `documentation`, enabling the AuthorizationCode and Password flow
- `dummy`, enabling the [*unsafe(?)*](https://tools.ietf.org/html/draft-ietf-oauth-security-topics-09) Implicit flow

After being fully recognized as a user, you can start uploading your fantastic images to the S3 cluster! (You may wanna take a look at the README to understand how it works!).
