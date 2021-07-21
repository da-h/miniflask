{theme=documentation}

\include{"../include.md"}

**The API is structured as follows**:
1. [**Miniflask Instance**](../../08-API/02-miniflask-Instance/)  
    covers the API of the caller script (or entrypoint) into miniflask modules as explained in the documentation part [Launching MiniFlask](../../02-Launching-MiniFlask/).
2. [**register(mf) Object**](../../08-API/03-register(mf\)-Object)  
    is the instance that is passed into every `def register(mf)` call upon module registration.
3. [**event**](../../08-API/04-event)  
    is the object that enables calls to any other loaded module.
3. [**state**](../../08-API/05-state)  
    manages the local and global variables of any loaded module.



----

**Full List of Contents**:
\listdocuments{dir="..", !collapseother}


