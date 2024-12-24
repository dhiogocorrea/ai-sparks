## Env Variables:

First of all, copy the `.env.template` file to `.env` and proceed to fill the needed variables.

### OpenAI:

We will need an openAI api key to access ChatGPT. OpenAI provides free credits to test in a fresh new account.


### HuggingFace:

To be able to run some models, like pyannote, you will need a huggingface account and accept the conditions of this two repos:

```
https://huggingface.co/pyannote/segmentation-3.0
```

```
https://huggingface.co/pyannote/speaker-diarization-3.0
```

```
https://huggingface.co/pyannote/speaker-diarization-3.1
```

Then, create an access token at:

```
https://huggingface.co/settings/tokens
```

And put it in the .env file as `HF_ACCESS_KEY`

---

## Required packages:

Install then via pip:

```
pip install -r requirements.txt
```

We are using:

- **pyannote.audio:** for speaker diarization.
- **pydub:** to convert mp4 to wav.
- **openai-whisper**: convert audio to text.
- **pandas**: to handle tabular data easily.