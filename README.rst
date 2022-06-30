dotfiles
========

My dotfiles (and scripts!) for some programs

Installation
============

::

    git clone
    cd dotfiles
    ./symlink_files.sh


pyenv
=====

::

   git clone https://github.com/pyenv/pyenv ~/.pyenv
   pyenv install 2.7.14
   pyenv install 3.6.4
   pyenv install miniconda2-latest
   pyenv install miniconda3-latest

   pyenv virtualenv 3.6.4 selenium
   pyenv activate selenium

   echo 2.7.14 > ~/.python-version

   pip install ipython bpython ipdb docker-compose


selenium
========

::

   wget https://github.com/mozilla/geckodriver/releases/download/v0.16.1/geckodriver-v0.16.1-linux64.tar.gz -O - | tar xvfz
   move geckodriver ~/bin


Archlinux packages
==================

Take a look at `pacman-pkg.txt`.
