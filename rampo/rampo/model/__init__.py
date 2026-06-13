__all__ = ["PeakPoModel", "PeakPoModel8"]


def __getattr__(name):
    if name in __all__:
        from .model import PeakPoModel, PeakPoModel8
        return {
            "PeakPoModel": PeakPoModel,
            "PeakPoModel8": PeakPoModel8,
        }[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
