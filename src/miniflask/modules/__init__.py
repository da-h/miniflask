
def registerPredefined(modules_avail):
    for m in ["modules", "events", "info", "settings"]:
        module_name_id = 'miniflask.'+m
        importpath = 'miniflask.modules.'+m
        modules_avail[module_name_id] = {
            'id': module_name_id,
            'importpath': importpath,
            'lowpriority': False
        }
