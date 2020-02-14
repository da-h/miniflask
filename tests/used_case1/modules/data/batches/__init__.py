def dataloader(state, event):
    ds = event.dataset()
    for i in range(state["size"]):
        ds_batch = event.optional.dataset_augment(ds)
        yield ds_batch+" Batch N°"+str(i)+ " of "+str(state.all["data.batches.size"])
    print(ds)

def register(mf):
    mf.register_defaults({
        "size": 4
    })
    mf.register_event("dataloader", dataloader, unique=True)
