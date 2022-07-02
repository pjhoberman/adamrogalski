# Installation
1. Open up terminal (the command line)
2. Make sure `pip` is installed.
   1. For windows, this line should check and install pip if it's not already installed:
   
      `C:> py -m ensurepip --upgrade`
   2. Full instructions can be found here: https://pip.pypa.io/en/stable/installation/
3. Download the code. This will create a directory in the directory you currently find yourself:
   1. `git clone git@github.com:pjhoberman/adamrogalski.git && cd adamrogalski`
4. Install requirements:
   1. `pip install --upgrade pip`
   2. `pip install -r requirements.txt`

# Usage
1. From within the `adamrogalski` directory in the terminal, run:
   1. `py -m main --state <state>` where <state> is the full name, lowercase, of the state you want to scrape.
   2. For example: `py -m main --state illinois`
   3. These scripts take a while to run. At the end, there will be a csv in the current directory with all the data, a pdf with the final output, and a folder with all the images.
