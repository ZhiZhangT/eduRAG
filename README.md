# eduRAG

## Getting started

1. Install all dependencies using `pip install -r requirements.txt`
2. Create a `.env` file with the following variables
```shell
OPENAI_MODEL=
MONGODB_URI=
OPENAI_API_KEY=
```
3. Start the server by running `uvicorn app.main:app --reload`

## Testing

### Prerequisite
Install promptfoo:
```shell
npx promptfoo@latest init
```

### Run end-to-end tests

1. `npx promptfoo@latest eval -c test/end_to_end/promptfooconfig.yaml --no-cache --output test.json`
2. To view logs / print statements while running evaluations, use `npx promptfoo@latest eval -c test/end_to_end/promptfooconfig.yaml --no-cache --verbose --output test.json`

### View evaluations
```shell
npx promptfoo@latest view
```