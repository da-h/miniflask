
def register(mf):  # noqa: C901 too-complex

    # defaults for all modules (queriable by all modules)
    mf.register_defaults({mf.module_id.split(".")[-1] + "_var": mf.state["number"]})
    mf.state["number"] += 1
