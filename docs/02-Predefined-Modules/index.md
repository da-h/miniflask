{theme=documentation}

\include{"../include.md"}


# Predefined Modules {section-contentlist=False}
MiniFlask comes with some simple Modules (that can be included at any time)


### Module `modules`
Yes, the first module is called `modules`.
It simply lists all available modules in a directory.

**Example Output:**
{.customsyntax}$$
Load Module ... \literal{miniflask.modules.modules}
\title{.}
├── flavours
│    └── \title{somedeps}
├── data
│    ├── \title{batches}
│    │    \meta{! dataloader}
│    └── \title{augment}
│         \meta{! dataset_augment}
├── datasets
│    ├── \title{cifar10}
│    │    \meta{! dataset}
│    └── \title{imagenet}
│         \meta{! dataset}
├── loops
│    └── \title{main_loop}
│         \meta{> main}
├── models
│    ├── \title{model2}
│    └── \title{model1}
└── \title{module3}
--------------------------------------------------
There is nothing to do.
$$

---

### Module `events`
This module shows all registered events of all available modules.

**Example Output:**
{.customsyntax}$$
Load Module ...\literal{ miniflask.modules.events}

\title{Available events}
\meta{! dataloader} used in \literal{data.batches}
\meta{! dataset used} in \literal{datasets.cifar10, datasets.imagenet}
\meta{! dataset_augment} used in \literal{data.augment}
\meta{> init} used in \literal{miniflask.modules.settings}
\meta{! main} used in \literal{loops.main_loop}
\meta{--------------------------------------------------}
There is nothing to do.
$$

---

### Module `settings`
This module shows all registered events of all available modules.

**Example Output:**
{.customsyntax}$$
Folder│\title{module}│\literal{variable} = value
—————————————————————————————
data│\title{augment}│\literal{fn}       = transform
    │\title{batches}│\literal{size}     = 4
loops│\title{main_loop}│\literal{epoch} = 2
--------------------------------------------------
$$

---

### Module `info`
Calls `modules` and then `events`.  
(Finishes the program afterwards.)

**Example Output:**
{.customsyntax}$$
Load Module ... \literal{miniflask.modules.modules}
\title{.}
├── flavours
│    └── \title{somedeps}
├── data
│    ├── \title{batches}
│    │    \meta{! dataloader}
│    └── \title{augment}
│         \meta{! dataset_augment}
├── datasets
│    ├── \title{cifar10}
│    │    \meta{! dataset}
│    └── \title{imagenet}
│         \meta{! dataset}
├── loops
│    └── \title{main_loop}
│         \meta{> main}
├── models
│    ├── \title{model2}
│    └── \title{model1}
└── \title{module3}
--------------------------------------------------

Load Module ...\literal{ miniflask.modules.events}

\title{Available events}
\meta{! dataloader} used in \literal{data.batches}
\meta{! dataset used} in \literal{datasets.cifar10, datasets.imagenet}
\meta{! dataset_augment} used in \literal{data.augment}
\meta{> init} used in \literal{miniflask.modules.settings}
\meta{! main} used in \literal{loops.main_loop}
\meta{--------------------------------------------------}
$$


