import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest
import matplotlib

# This is needed to prevent matplotlib from trying to use the X server
matplotlib.use('Agg')


@pytest.fixture
def mock_all_ophyd_devices():
    """
    Mock EpicsSignalBase methods to prevent any EPICS connections.
    All signals return 0 for reads and do nothing for writes.
    """
    import ophyd

    @classmethod
    def cls_noop(cls, *args, **kwargs):
        return
    
    def noop(self, *args, **kwargs):
        return
    
    def mock_get(self, *args, **kwargs):
        return 0
    
    def mock_subscribe(self, *args, **kwargs):
        return 0
    
    # Mock connected property to always return True
    @property
    def mock_connected(self):
        return True

    # Save originals
    originals = {
        'Device.wait_for_connection': ophyd.Device.wait_for_connection,
        'Device.connected': getattr(type(ophyd.Device), 'connected', None),
        'EpicsSignal.wait_for_connection': ophyd.signal.EpicsSignal.wait_for_connection,
        'EpicsSignalBase.wait_for_connection': ophyd.signal.EpicsSignalBase.wait_for_connection,
        'EpicsSignalBase.connected': getattr(type(ophyd.signal.EpicsSignalBase), 'connected', None),
        'EpicsSignalBase.get': ophyd.signal.EpicsSignalBase.get,
        'EpicsSignalBase.put': ophyd.signal.EpicsSignalBase.put,
        'EpicsSignalBase.subscribe': ophyd.signal.EpicsSignalBase.subscribe,
        'EpicsSignalBase.set': ophyd.signal.EpicsSignalBase.set,
        'EpicsSignalBase.set_defaults': ophyd.signal.EpicsSignalBase.set_defaults,
    }

    # Apply mocks
    ophyd.Device.wait_for_connection = noop
    ophyd.Device.connected = mock_connected
    ophyd.signal.EpicsSignal.wait_for_connection = noop
    ophyd.signal.EpicsSignalBase.wait_for_connection = noop
    ophyd.signal.EpicsSignalBase.connected = mock_connected
    ophyd.signal.EpicsSignalBase.get = mock_get
    ophyd.signal.EpicsSignalBase.put = noop
    ophyd.signal.EpicsSignalBase.subscribe = mock_subscribe
    ophyd.signal.EpicsSignalBase.set = noop
    ophyd.signal.EpicsSignalBase.set_defaults = cls_noop
    
    yield
    
    # Restore originals
    ophyd.Device.wait_for_connection = originals['Device.wait_for_connection']
    if originals['Device.connected'] is not None:
        type(ophyd.Device).connected = originals['Device.connected']
    ophyd.signal.EpicsSignal.wait_for_connection = originals['EpicsSignal.wait_for_connection']
    ophyd.signal.EpicsSignalBase.wait_for_connection = originals['EpicsSignalBase.wait_for_connection']
    if originals['EpicsSignalBase.connected'] is not None:
        type(ophyd.signal.EpicsSignalBase).connected = originals['EpicsSignalBase.connected']
    ophyd.signal.EpicsSignalBase.get = originals['EpicsSignalBase.get']
    ophyd.signal.EpicsSignalBase.put = originals['EpicsSignalBase.put']
    ophyd.signal.EpicsSignalBase.subscribe = originals['EpicsSignalBase.subscribe']
    ophyd.signal.EpicsSignalBase.set = originals['EpicsSignalBase.set']
    ophyd.signal.EpicsSignalBase.set_defaults = originals['EpicsSignalBase.set_defaults']


@pytest.fixture
def mock_services():
    with patch("redis.Redis", return_value=MagicMock()), \
         patch("tiled.client.from_profile", return_value=MagicMock()), \
         patch("tiled.client.from_uri", return_value=MagicMock()), \
         patch("pyOlog.SimpleOlogClient", return_value=MagicMock()):
        os.environ["TILED_BLUESKY_WRITING_API_KEY_IXS"] = "mocked_api_key"
        yield
    del os.environ["TILED_BLUESKY_WRITING_API_KEY_IXS"]

@pytest.fixture
def mock_nslsii():
    def mock_configure_base(ipython_user_ns, beamline_name, **kwargs):
        from bluesky.callbacks.best_effort import BestEffortCallback
        ipython_user_ns["RE"] = MagicMock()
        ipython_user_ns["sd"] = MagicMock()
        ipython_user_ns["bec"] = BestEffortCallback()
        

    def mock_configure_kafka_publisher(run_engine, beamline_name, **kwargs):
        ...

    with patch("nslsii.configure_base", side_effect=mock_configure_base), \
         patch("nslsii.configure_kafka_publisher", side_effect=mock_configure_kafka_publisher):
        yield


@pytest.fixture
def startup_dir():
    profile_dir = Path(__file__).parent.parent
    startup_dir = profile_dir / "startup"
    sys.path.insert(0, str(startup_dir))
    yield startup_dir
    sys.path.remove(str(startup_dir))

from unittest.mock import patch, mock_open, MagicMock
from pathlib import Path

@pytest.fixture
def mock_sixcircle_config():
    """Mock configuration file loading for SixCircle"""
    mock_config_content = """# Configuration file
GLOBAL g_sample TestSample
GLOBAL g_haz 0.0
GLOBAL g_kaz 0.0
GLOBAL g_laz 1.0
GLOBAL g_aa 5.0
GLOBAL g_bb 5.0
GLOBAL g_cc 5.0
GLOBAL g_al 90.0
GLOBAL g_be 90.0
GLOBAL g_ga 90.0
GLOBAL g_h0 1.0
GLOBAL g_k0 0.0
GLOBAL g_l0 0.0
GLOBAL g_u00 0.0
GLOBAL g_u01 0.0
GLOBAL g_u02 0.0
GLOBAL g_u03 0.0
GLOBAL g_u04 0.0
GLOBAL g_u05 0.0
GLOBAL g_h1 0.0
GLOBAL g_k1 1.0
GLOBAL g_l1 0.0
GLOBAL g_u10 0.0
GLOBAL g_u11 0.0
GLOBAL g_u12 0.0
GLOBAL g_u13 0.0
GLOBAL g_u14 0.0
GLOBAL g_u15 0.0
GLOBAL g_lambda0 1.5418
GLOBAL g_lambda1 1.5418
GLOBAL L_TTH -180.0
GLOBAL U_TTH 180.0
GLOBAL L_TH -180.0
GLOBAL U_TH 180.0
GLOBAL L_CHI -180.0
GLOBAL U_CHI 180.0
GLOBAL L_PHI -180.0
GLOBAL U_PHI 180.0
GLOBAL L_MU -180.0
GLOBAL U_MU 180.0
GLOBAL L_GAM -180.0
GLOBAL U_GAM 180.0
GLOBAL L_ALPHA -180.0
GLOBAL U_ALPHA 180.0
GLOBAL L_BETA -180.0
GLOBAL U_BETA 180.0
"""
    
    original_open = open
    
    def mock_open_func(filepath, *args, **kwargs):
        # If it's a sixcircle config file, return mock content
        if isinstance(filepath, str) and (
            'sixcircle' in filepath or 
            'ini.conf' in filepath or
            'dia_test.conf' in filepath or
            filepath.startswith('/IXS2/') or
            filepath.startswith('/nsls2/')
        ):
            from io import StringIO
            return StringIO(mock_config_content)
        # Otherwise use the real open
        return original_open(filepath, *args, **kwargs)
    
    with patch('builtins.open', side_effect=mock_open_func):
        yield

@pytest.fixture
def startup_shell(mock_all_ophyd_devices, mock_services, mock_nslsii, mock_sixcircle_config, startup_dir):
    from IPython.core.interactiveshell import InteractiveShell
    from IPython.core.profiledir import ProfileDir

    # Use the project directory as the profile directory (like --profile-dir=.)
    project_dir = startup_dir.parent
    profile_dir = ProfileDir(location=str(project_dir))
    
    shell = InteractiveShell.instance(profile_dir=profile_dir)
    
    try:
        with patch("builtins.input", return_value="SMI"):
            for file in sorted(startup_dir.glob("*.py")):
                print(f"Running {file}")
                with open(file, "r") as f:
                    code = f.read()
                result = shell.run_cell(code, store_history=True, silent=True)
                result.raise_error()

            globals().update(shell.user_ns)
            yield shell
    finally:
        InteractiveShell.clear_instance()

def test_startup_namespace(startup_shell):
    assert "RE" in globals(), "RunEngine not found"
    assert "bec" in globals(), "BestEffortCallback not found"
