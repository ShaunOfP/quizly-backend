# Quizly

Quizly is a platform, where you can generate a Quiz out of a Youtube-Link.

This repository contains the backend for the Quizly-Project. The Frontend is provided by the Developer Akademie and can be found here: https://github.com/Developer-Akademie-Backendkurs/project.Quizly

## Installation

Clone the repository to your computer via git bash.

```bash
git clone https://github.com/YOUR-USERNAME/YOUR-REPOSITORY Path-of-the-Project
cd quizly-backend
```
A detailed guide to cloning a repository can be found [here](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository)

## Usage

Open the project in your Code editor and open the Terminal for the project. 

Create a virtual environtment in the project folder
```bash
python -m venv env
```

Then start a virtual environment:
```bash
#Windows
.\env\Scripts\Activate
```

```bash
#Unix
source .env/bin/activate
```

To use the project you need three things:

1. [yt-dlp](https://github.com/yt-dlp/yt-dlp): This technology is used to exctract and download the audio (.mp3) file from the provided Youtube-Video.
2. [whisper](https://github.com/openai/whisper): Developed by OpenAI, this tool creates a transcript of the extracted audio file.
3. [gemini](https://ai.google.dev/gemini-api/docs): Googles API is used to create the quiz from the provided transcript. To use Gemini you need to provide an API-Key, which can be generated on the given website. 

After you generated your API-Key, open a Terminal which runs the bash-console and enter the following command:
```bash
cp .env.template .env
```
This will generate the .env-file, where you **must** enter your API Key.

All needed dependencies are provided in a requirements.txt within the project. Use the package manager [pip](https://pypi.org/project/pip/#files) to install the dependencies.

```bash
pip install -r requirements.txt
```

Then you need to generate the database:
```bash
#Creates the data structures and models
python manage.py makemigrations

#Creates the database using the data and models generated previously
python manage.py migrate
```

After installing the dependencies and creating your database you can now start the backend:
```bash
#Windows & Unix
python manage.py runserver
```

To use this project without the Frontend you need to have software like [Postman](https://www.postman.com/downloads/).


## Authentication
Note: The Project uses [JWT](https://github.com/jazzband/djangorestframework-simplejwt) (JSON Web Token) for the authentication

### Registration
Register your user.

Endpoint: localhost/api/register/

HTTP-Method: POST

Request-body:
```python
{
  "username": "your_username",
  "password": "your_password",
  "confirmed_password": "your_confirmed_password",
  "email": "your_email@example.com"
}
```

### Login
Login with your created account. This will create two Tokens: the access-token and the refresh-token which will be needed for the authentication process. 

The generated access_token will be valid for 30 minutes after logging in. The refresh_token will be valid for 24 hours.

Note: If you use Postman, in the Headers-Tab you need "Authorization" as Key and "Bearer access_cookie" to authenticate.

Endpoint: localhost/api/login/

HTTP-Method: POST

Request-body:
```python
{
  "username": "your_username",
  "password": "your_password"
}
```

### Logout
This will delete **both** cookies permanently. You will need to Login again if you want new cookies.

Endpoint: localhost/api/logout/

HTTP-Method: POST

Permissions: You need to be authenticated to use this endpoint.

Request-body: not needed

### Token refreshing
Here you can refresh your access_token once it is expired.

Endpoint: localhost/api/token/refresh/

HTTP-Method: POST

Permissions: You need to be authenticated to use this endpoint.

Request-body: not needed

## Quiz Management
Here you can read about creating, managing and infos about Quizzes.

### Creating a Quiz
You provide a Youtube-Link and get a Quiz back. You can use either the normal Youtube-Urls or the shorter shared variants. Both will work.

Endpoint: localhost/api/createQuiz/

HTTP-Method: POST

Permissions: You need to be authenticated to use this endpoint.

Request-body:
```python
{
  "url": "https://www.youtube.com/watch?v=example"
}
```

### Quiz List
Here you will see a list with all of quizzes, which are created by **you**.

Endpoint: localhost/api/quizzes/

HTTP-Method: GET

Permissions: You need to be authenticated to use this enpoint.

Request-body: not needed

### Managing quizzes
Here you can get infos about a specific quiz, update existing ones or delete a quiz completely.

#### 1. Inspecting a specific quiz
Endpoint: localhost/api/quizzes/{id}/

HTTP-Method: GET

Permissions: You need to be authenticated to use this endpoint. You will only see **your** quizzes.

Request-body: not needed

#### 2. Updating an existing quiz
Endpoint: localhost/api/quizzes/{id}/

HTTP-Method: PATCH

Permissions: You need to be authenticated to use this endpoint. You will only change/update **your** quizzes.

Request-body:
```python
{
  "title": "Partially Updated Title"
}
```

#### 3. Deleting a quiz
**IMPORTANT**: Deleting a quiz is permanent and can't be undone.

Endpoint: localhost/api/quizzes/{id}/

HTTP-Method: DELETE

Permissions: You need to be authenticated to use this endpoint. You will only delete **your** quizzes.

Request-body: not needed

## Contributing

It is not intended to contribute to this repository.

## License

[MIT](https://choosealicense.com/licenses/mit/)
