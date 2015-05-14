=================
Performance Tools
=================

:Version: 0.2.0
:Status: beta
:Author: José Antonio Perdiguero López

Some tools to make performance analysis and improvements.

Tools
=====

URLs Flow
---------
Extract a complete url flow from different sources like nginx logs. This sources can be stored in different platforms, Elasticsearch as a example.

Times
-----
Different tools to measure times that are spent loading urls.

Digraph
-------
Represent a complete URL flow using a digraph, with tools to draw, make subgraphs, find paths and some others.

Install
=======
Install system requirements (On Ubuntu)::

    sudo apt-get install -y build-essential libblas-dev liblapack-dev libatlas-dev libatlas-base-dev python-dev gfortran
    sudo apt-get build-dep -y python-matplotlib
    sudo apt-get install -y libzmq-dev
    sudo apt-get install ipython-notebook
    
Make a virtualenv::

    pip install virtualenv virtualenvwrapper
    echo "source /usr/local/bin/virtualenvwrapper.sh" >> ~/.bashrc
    echo "export WORKON_HOME=$HOME/.virtualenvs" >> ~/.bashrc
    mkvirtualenv scienv
    
Install SciPy stack::
    
    sudo apt-get install gfortran libopenblas-dev liblapack-dev
    pip install numpy scipy matplotlib pandas

Install python requirements::

    pip install -r requirements.txt
