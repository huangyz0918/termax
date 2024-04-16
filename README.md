# Termax

![](https://github.com/huangyz0918/termax/actions/workflows/lint.yml/badge.svg) ![](https://github.com/huangyz0918/termax/actions/workflows/test.yml/badge.svg) ![PyPI - Version](https://img.shields.io/pypi/v/termax)
![PyPI - Downloads](https://img.shields.io/pypi/dm/termax) ![GitHub License](https://img.shields.io/github/license/huangyz0918/termax)

Termax is an LLM agent in your terminal that converts natural language to commands.

<br/>
<p align="center"> <img src="docs/icon_text.svg" alt="..." width=300>

It is featured by:

- 🍼 Personalized Experience: Optimize the command generation with RAG.
- 📐 Various LLMs Support: OpenAI GPT, Anthropic Claude, Google Gemini, Mistral AI, and more.
- 🧩 Shell Extensions: Plugin with popular shells like `zsh`, `bash` and `fish`.
- 🕹 Cross Platform: Able to run on Windows, macOS, and Linux.

## Installation

```bash
pip install termax
```

## Quick Start

> [!TIP]
> * After installation, you'll need to configure the LLM (e.g., set the [OpenAI API key](https://beta.openai.com/account/api-keys)).
> * A setup guide will automatically launch the first time you use Termax. 
> * Alternatively, you can manually initiate configuration at any time by running `t config` or `termax config`.


#### Ask Commands

You can start using Termax by asking using command `t` or `termax`, for example:

```bash
t show me the top-5 CPU processes
```

You can also use Termax to control your software:

```bash
t play a song using Spotify
```

Here is a more complex example:

![](docs/ask_cmd.gif)

#### Guess Commands (experimental)

Termax can predict your next move based on your command history —just try `t guess` or `termax guess` to generate a suggested
command. It's not only smart, it's fun!

```bash
t guess
```

## Shell Plugin

We support various shells like `bash`, `zsh`, and `fish`. You can choose to install the plugins by:

```bash
t install -n <plugin>
```

The `<plugin>` can be any of `zsh`, `bash`, or `fish`. With this plugin, you can directly convert natural language into
commands using the `Ctrl + K` shortcut.

![](docs/plugin.gif)

You can also easily uninstall the plugin by:

```bash
t uninstall -n <plugin>
```

Remember to source your shell or restart it after installing or uninstalling plugins to apply changes.

## Configuration

Termax has a global configuration file that you can customize by editing it. Below is an example of setting up Termax with OpenAI:

```
[general]                  # general configuration
platform = openai          # default platform
auto_execute = False       # execute the generated commands automatically
show_command = True        # show the generated command
storage_size = 2000        # the command history's size, default is 2000

[openai]                   # platform-related configuration
model = gpt-3.5-turbo      # LLM model
api_key = <your API key>   # API key
temperature = 0.7
save = False
```

> [!TIP]
> * The configuration file is stored at `<HOME>/.termax`, so as the vector database.
> * We utilize [ChromaDB](trychroma.com) as the vector database. When using OpenAI, Termax calculates embeddings with OpenAI's `text-embedding-ada-002`. For other cases, we default to Chroma's built-in model.


## Contributing

For developers, you can install from source code to enable the latest features and bug fixes.

```bash:
cd <root of this project>
pip install -e .
```

We are using [PEP8](https://peps.python.org/pep-0008/) as our coding standard, please read and follow it in case there
are CI errors.

## License

Licensed under the [Apache License, Version 2.0](LICENSE).





