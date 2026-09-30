import sys
import types

# Windows AppLocker policy may block pyarrow C++ DLL (pyarrow.lib).
# If pyarrow fails to import its native DLLs, install a lightweight compatibility shim
# so pandas and scikit-learn operate gracefully without failing on AppLocker policy.
try:
    import pyarrow
except ImportError:
    pa = types.ModuleType("pyarrow")
    pa.__version__ = "0.0.0"
    class _DummyType: pass
    pa.Table = _DummyType
    pa.RecordBatch = _DummyType
    pa.Array = _DummyType
    pa.ChunkedArray = _DummyType
    pa.DataType = _DummyType
    sys.modules["pyarrow"] = pa
