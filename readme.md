# asr-annotation-bot

Simple Telegram bot to varify Automatic Speech Recognition (ASR) dataset annotations

## Motivation

I know that there exist a great number of annotation tools including the ones written by me, but I feel tired from configuring them and telling annotators how to use them. So I wanted to use an interface that is familiar and accessible to anyone and anytime. And, Telegram did a great job. It didn't take even 20 mins to write the whole code (in fact, it was shorter than the time spent to publish this repo). I'm sharing this simple code hoping that it may be an inspiration for others to develop Telegram bots to annotate data for other machine learning tasks.
## How to use
The only dependency is `python-telegram-bot` which is pip-installable:
```shell
pip install python-telegram-bot
```

the code is simple and self-explanatory with short and useful comments. Basically you need to obtain an API token from Bot Father on Telegram and update `TOKEN` variable with that one in `annotationbot.py`. Second, prepare your dataset in a LJSpeech-like format with a few changes:
- Audio files should be kept in Opus format as Telegram excepts voice files in this format.
- `metadata.csv` file should contain one sample on a line with file name and unvarified annotation separated with a single pipe character (|).

After everythin is ready, you can simply run:
```shell
python annotationbot.py
```

Go to Telegram and send `/start` to start talking to your bot.

## See also
You may also want to take a look at my other audio annotation tool called [label-snd](https://github.com/monatis/label-snd).