# eduRAG

## Getting started

1. Install all dependencies using `pip install -r requirements.txt`
2. Create a `.env` file with the following variables
```shell
MONGODB_URI=
```
3. Start the server by running `uvicorn app.main:app --reload`

## Testing

### Prerequisite
Install promptfoo:
```shell
npx promptfoo@latest init
```

### Run end-to-end tests

1. `npx promptfoo@latest eval -c test/end_to_end/promptfooconfig.yaml --no-cache`
2. To view logs / print statements while running evaluations, use `npx promptfoo@latest eval -c test/end_to_end/promptfooconfig.yaml --no-cache --verbose`

### View evaluations
```shell
npx promptfoo@latest view
```