def register(mf):  # noqa: C901 too-complex
    current_level = len(mf.module_id.split(".")) - 1

    # defaults for all modules (queriable by all modules)
    defaults = {
        "filename": __file__
    }

    # local variable query:
    # - explicit: .filename
    # - implicit:  filename
    def get_local_var(state, explicit=False):
        if explicit:
            print("testing for: .filename from", mf.module_id)
            return state[".filename"]
        print("testing for: filename from", mf.module_id)
        return state["filename"]
    mf.register_event("get_local_var", get_local_var, unique=False)

    # global variable query:
    # - explicit: filename_level0
    # - implicit: .filename_level0
    def get_global_var(state, explicit=False):
        if explicit:
            print("testing for: filename_level0 from", mf.module_id)
            return state["filename_level0"]
        print("testing for: .filename_level0 from", mf.module_id)
        return state[".filename_level0"]
    mf.register_event("get_global_var", get_global_var, unique=False)

    # fuzzy child variable query:
    # - explicit: .fuzzy
    # - implicit: fuzzy
    def get_fuzzy_child_var(state, explicit=False):
        if explicit:
            print("testing for: fuzzy from", mf.module_id)
            return state[".fuzzy"]
        print("testing for: .fuzzy from", mf.module_id)
        return state["fuzzy"]
    mf.register_event("get_fuzzy_child_var", get_fuzzy_child_var, unique=False)

    # fuzzy child (non-unique) variable query:
    # - explicit: .fuzzychild_nonunique
    # - implicit: fuzzychild_nonunique
    def get_fuzzy_child_nonunique_var(state, explicit=False):
        if explicit:
            print("testing for: fuzzychild_nonunique from", mf.module_id)
            return state[".fuzzychild_nonunique"]
        print("testing for: .fuzzychild_nonunique from", mf.module_id)
        return state["fuzzychild_nonunique"]
    mf.register_event("get_fuzzy_child_nonunique_var", get_fuzzy_child_nonunique_var, unique=False)

    # nonexistent variabl query:
    def get_nonexistent_var(state):
        return state["nonexistent"]
    mf.register_event("get_nonexistent_var", get_nonexistent_var, unique=False)

    # create defaults for variables: one/two level/s up
    defaults["filename_level%i" % current_level] = __file__
    if current_level > 1:
        def get_parent_var(state, explicit=False):
            if explicit:
                print("testing for: ..filename from", mf.module_id)
                return state["..filename"]
            print("testing for: filename_level%i from" % (current_level - 1), mf.module_id)
            return state["filename_level%i" % (current_level - 1)]
        mf.register_event("get_parent_var", get_parent_var, unique=False)
    if current_level > 2:
        def get_parent_parent_var(state, explicit=False):
            if explicit:
                print("testing for: ...filename from", mf.module_id)
                return state["...filename"]
            print("testing for: filename_level%i from" % (current_level - 2), mf.module_id)
            return state["filename_level%i" % (current_level - 2)]
        mf.register_event("get_parent_parent_var", get_parent_parent_var, unique=False)

    mf.register_defaults(defaults)
