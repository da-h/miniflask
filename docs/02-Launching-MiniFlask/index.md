{theme=documentation}

# Launching MiniFlask
Things to do in the launch file.

\include{"../include.md"}


## Launch file

The first step in creating a new MiniFlask project is to create the launch file. The launch file initializes MiniFlask and tells it where modules are located. 
**Typically, you will never need to touch this file ever again!**

The following function calls have to be included:  
**Example file:** do.py
```python
import miniflask

# tells MiniFlask where the modules are located
# simply feed it a list of module folders
mf = miniflask.init(["module_collection_1","module_collection_2"])

# Parses arguments from the command line and runs the modules that have been specified
# as entrypoints. The run command first launches the `init` event if it exists and then
# the `main` events of all modules. If multiple modules with a main method are loaded,
# the main methods are executed in the order modules are specified using the CLI.
mf.run()
```

## Executing the launch file
In order to start our MiniFlask project, simply execute the `do.py` file and list all modules to load separated by a comma. To overwrite the default arguments, simply pass the new parameters precising the modules after the modules.

```python
> python main.py module2,module1 --module2.var 9001
main event called by module2
it uses a variable var: 9001
main event called by module1
```
