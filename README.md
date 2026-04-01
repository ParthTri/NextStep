# NextStep

NextStep is a web-based job application tracker. This was mainly just a side project, thrown together over a couple of days, to take the pain away of managing dozens of job applications on a spreadsheet.

Hope it helps you too.

## Features

- Input and track job applicatinos (pretty basic)
- View all the applications in an easy to see dashboard
- Connect with your email provider (Gmail is only really supported right now) and automatically update the statuses of your applications.

You can go through the images [here](./docs/images.md).

## Installation

The easiest way to deploy this is with `docker` and `docker compose`, so this assumes you have docker installed on your system to deploy.

1. Clone the repository
```sh
git clone https://github.com/ParthTri/NextStep.git
```

2. Navigate into the directory
```sh
cd NextStep
```

3. Make sure to set the environment variables using command line tools. Here you can set the `DJANGO_SECRET` and `ENCRYPTION_KEY`.
```sh
openssl rand -hex 64  # for DJANGO_SECRET
openssl rand -base64 32 # For ENCRYPTION_KEY
```

4. Docker Pull to get the images. **NOTE** This may take a while to download all the images and build all the container images.
```sh
docker compose pull
```

5. Build and start the containers
```sh
docker compose up -d --build
```

## Usage

Once you've installed and started using the docker compose file, you can navigate to `{IP_ADDRESS}:8000/signup` and create a user account. Upon creation you will be redirected to the dashboard page where you can start adding all your applications.

### Linking Emails from Google

To link your emails with Google (only one supported right now) you will need to first go to [console.cloud.google.com](https://console.cloud.google.com), and register to use OAuth 2.0 Client.

You can follow these general steps to register a client.

1. Go to the Credentials tab of the API & Services section
2. Click on the "Create Credentials" wizard, with OAuth client ID
3. Set the application as a "Web Application"
4. Set the name to something memorable (I used NextStep)
5. However you plan on running it off server, with a static IP address or domain name, use this for the "Authorized redirect URIs". Add the following URIs:
- `http://{Domain name or IP}/`
- `http://{Domain name or IP}/connect/oauth`
- `http://{Domain name or IP}/connect/google`

Be sure to set the folowing environment variables:
```
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
```
