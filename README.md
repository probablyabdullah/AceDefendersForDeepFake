# README

### What is this repository for?

- TruthGuard:

### How do I get set up?

- Add deepfake detection files to the `temp/` folder
- Ensure all the dependencies are installed
- set up `config.py` with the following string:

```
gemini_api_key = "<your api key here>"
pinecone_api_key = "<your api key here>"
google_api_key = "<your api key here>"
fact_check_api_key = "<your api key here>"
openai_api_key = "<your api key here>",
openai_organization = "<your api key here>"
serpapi_api_key = "<your api key here>"
```

- Run the cache server with `python cache_server.py`
- Run the api server with `python ai_server.py`

_It was noticed that the `pytube` module is having continuous issues. We have implemented temporary fixes, but it may not work in the future. More information on fixes can be found on the [`pytube` github page](https://github.com/pytube/pytube)_
