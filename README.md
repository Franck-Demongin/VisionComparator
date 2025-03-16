![hero_vision-comparator_0 1 0](https://github.com/user-attachments/assets/682347c9-e247-4bb5-9754-7f86a7593d52)

<img src="https://img.shields.io/badge/Python-3.10-blue" /> ![Static Badge](https://img.shields.io/badge/Ollama-0.6.0-blue) ![Static Badge](https://img.shields.io/badge/Streamlit-1.42.0-blue) [![GPLv3 license](https://img.shields.io/badge/License-GPLv3-green.svg)](http://perso.crans.org/besson/LICENSE.html)

# Vision Comparator

<img src="https://img.shields.io/badge/Version-0.2.0-blue" />

Vision Comparator lets you test and compare multi-models with the vision capabilities available with Ollama.

It allows you to:

- submit an image to several models and several prompts simultaneously to compare results.
- download the results as JSON
- manage models:
  - list of models supporting vision functionalities
  - pull, update, delete
- manage the prompts used (Select, Create, Update, Delete).
- display JSON results.

## Installation

Install ollama  
Go to [ollama.com](https://ollama.com/) and follow the instructions to install it on your system. Ollama is available for Windows, Mac and Linux.

If GIT is installed, open a terminal where you want install it and type:

```bash
git clone https://github.com/Franck-Demongin/VisionComparator.git
```

If GIT is not installed, retrieve the [ZIP](https://github.com/Franck-Demongin/VisionComparator/archive/refs/heads/main.zip) file, unzip it into where you want install it. Rename it VisionComparator.

Open a terminal in the folder VisionComparator.  
Create a virtual env to isolate dependencies:

```bash
python -m venv .venv
```

_python_ should be replace by the right command according to your installation. On Linux, it could be _python3.10_ (or 3.11), on Windows _python.exe_

Activate the virtual environmant:

```bash
# Windows
.venv\Scripts\activate

# Linux
source .venv/bin/activae
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### Update

If VisionComparator has been installed with GIT, open a terminal in this directory and type:

```bash
git pull
```

If it was downloaded as a ZIP archive, download the new ZIP version, save the file _prompt_user.json_ (to preserve your prompts), delete the directory and reinstall it.

Re-install the dependencies:

```bash
pip install -U -r requirements.txt
```

## Usage

Open a terminal in the folder VisionComparator.  
Activate the virtual environmant:

```bash
# Windows
.venv\Scripts\activate

# Linux
source .venv/bin/activate
```

Run the application:

```bash
streamlit run app.py
```

Open your browser and navigate to [http://localhost:8501](http://localhost:8501)

### Compare models

To test and compare models, select one or more models, choose one or more prompts and an image to compare the results.

At the end of the session, the statistics are displayed and you can download the results as JSON.

### Manage models

To manage models, go to the _Models_ page.

The first section, **List of models with vision support**, displays the list of models with vision support.
For a model downloaded with Ollama to be recognized, its name must appear in this list.  
Use the “Edit” button to modify the list of models.

The **Models available** section displays compatible models already present on your system. This is the list of models available for testing in VisionComparator.

You can download a model directly from this page.
You can also update or delete a model already downloaded.

### Manage prompts

To manage prompts, go to the _Prompts_ page.

Each prompt has a name, a description, a system prompt and a prompt.
You can create, update or delete prompts.

To restore the list of default prompts, click on the _Refresh_ button.

### View results saved as JSON

To view the results saved as JSON, go to the _Viewer_ page and load a JSON file.

## License

This project is released under the [GPLv3 license](http://perso.crans.org/besson/LICENSE.html)

## Changelog

### 0.2.0 - 2025-03-16

**New features:**

- Compare models with multiple prompts
- Download results as JSON
- Display Statistics
- View results saved as JSON

**Bug fixes:**

- Fix bug when adding a prompt with the same name or whith a blank name
- Fix bug when renaming a prompt

### 0.1.0 - 2025-03-10

**First release:**

- Compare models
- List of models with vision support
- Create, update and delete prompts
