How to Play
============

Installation
-------------

Compatible with python2.7, no python3 at the moment, because of twisted

No script or eggfile at the moment, you have to clone or download this repository. Don't forget to install the requirements with "pip install -r requirements.txt"

Commandline
------------

Start game with "python todesknobel.py --cmd"

Commands:

d - roll dice  
s [1,2,3,4,5] - save die and display status of all dice, you can use a comma-seperated list (without braces)  
p - show points of current player  
p_all - show points of all players  
point commands - see below, assign current values to point fields:

one
two
three
four
five
six
threesome
foursome
fullhouse
kniffel
small_street
big_street
chance

Webserver
----------

You can play todeskniffel in a web application using websockets. Just type "python todeskniffel.py --server" and deploy the web application located in "webclient/" somewhere. Copy the configuration files "wsconfig.py.dist" to "wsconfig.py" and "webclient/js/tkclient/config.js.dist" to "webclient/js/tkclient/config.js". Adjust parameters.
