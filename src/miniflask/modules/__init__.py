
def registerPredefined(modules_avail):
    for m in ["modules", "events", "info", "settings", "definitions"]:
        module_name_id = 'miniflask.' + m
        importname = 'miniflask.modules.' + m
        modules_avail[module_name_id] = {
            'id': module_name_id,
            'importpath': "system",
            'importname': importname,
            'lowpriority': False
        }
