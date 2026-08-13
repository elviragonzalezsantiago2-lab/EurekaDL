def test_import_core():
    import importlib
    importlib.import_module('orpheus')
    importlib.import_module('eureka')
    importlib.import_module('modules.youtube.interface')
    importlib.import_module('modules.spotify.interface')
    importlib.import_module('modules.deezer.interface')
    importlib.import_module('modules.soundcloud.interface')
    importlib.import_module('modules.bandcamp.interface')
    assert True
