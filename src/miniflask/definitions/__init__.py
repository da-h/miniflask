
def register(mf):
    mf.load("settings")
    mf.overwrite_globals({
        "settings.show_registration_definitions": True
    })
