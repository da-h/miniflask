{theme=documentation}



# Modules
\include{"../include.md"}

Modules represent the core functionality of miniflask. Modules encapsulate a given feature (e.G. Batch Normalization or ReLU) and can be internchaged at will (e.G. use Group Normalization instead of Batch Normalization) witout any additional code changes. Modules contain methods that can be attached to hooks in the main method or other methods (see [Register Events](07-Register-Events.md)).

Every module is identified by its unique ID (scope) given by its folder structure. A module located in ``modules/module1/submodule2/subsubmodule2`` is identified by its ID ``module1.submodule2.subsubmodule2``.


### Minimal requirements

..for a MiniFlask module

A folder has to contain at least the following files to be recognised as a MiniFlask module : `__init__.py` and  `.module`. Inside `__init.py__`, a function `register(mf)` has to be reclared (ref. [Register Module Settings](06-Module-Declaration.md)).


