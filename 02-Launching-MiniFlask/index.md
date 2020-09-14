{theme=documentation}

# Launching MiniFlask

\include{"../include.md"}


## Launch file

	The first step in creating a new MiniFlask project is to create the launch file. The launch file initializes MiniFlask and tells it where modules are located. The following function calls have to be included :

**Example file:** do.py
```python
import miniflask

mf = miniflask.init(["module_collection_1","module_collection_2"])
# or minifilask.init({"module1_altname": "./module1, "module2_altname": "./module2"})
mf.parse_args()
mf.run()
``` 

**miniflask.init(\*args)** tells MiniFlask where the modules are located : simply feed it a list of module folders. If name conflicts emerge, it is possible to feed it a dictionary with module aliases as keys and folder names.

**mf.parse\_args()** parses argument overwrites from the command line (see [Argument Parser](../03-Modules/06-Module-Declaration.md)).

**mf.run()** launches MiniFlask. The run command first launches the `init` event if it exists and then the `main` events of all modules. If multiple modules with a main method are loaded, the main methods are executed in the order modules are loaded).

## Launching the launch file

In order to start our MiniFlask project, simply execute the do.py file and precise all modules to load separated by a comma. To overwrite the default arguments, simply pass the new parameters precising the modules after the modules (see [Arument Parser](../03-Modules/06-Module-Declaration.md)).

```python
> python main.py module2,module1 --module2.var 9001
main event called by module2
it uses a variable var: 9001
main event called by module1
```

{.alert}
Note: it is possible to shorten variable identifiers (leave out the module name) as long as they are unambigous (fuzzy search). 
