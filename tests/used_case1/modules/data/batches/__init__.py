from colored import fg


def dataloader(state, event):
    ds = list(event.dataset())
    for i in range(len(ds) // state["size"]):
        batch = ds[i * state["size"]:(i + 1) * state["size"]]
        batch = event.optional.dataset_augment(batch, altfn=lambda x: x)
        yield fg('blue') + "".join(batch) + fg('white') + " Batch N°" + str(i) + " of " + str(state.all["modules.data.batches.size"])


def register(mf):
    mf.register_defaults({
        "size": 4
    })
    mf.register_event("dataloader", dataloader, unique=True)
