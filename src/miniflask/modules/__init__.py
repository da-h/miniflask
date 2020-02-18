
def registerPredefined(modules_avail):
    for m in ["modules", "events", "info", "settings"]:
        modules_avail["miniflask.modules."+m] = modules_avail[m] = 'miniflask.modules.'+m
