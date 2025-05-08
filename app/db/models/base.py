# --- START - app/db/models/base.py ---

from sqlalchemy.orm import DeclarativeBase, class_mapper
from sqlalchemy.inspection import inspect as sa_inspect

# 1. Define the Mixin with the desired functionality
class ReprMixin:
    """Mixin class to add a standard __repr__ to SQLAlchemy models."""
    def __repr__(self) -> str:
        # Get the inspector for the instance
        inspector = sa_inspect(self)
        # Handle cases where the object might not be associated with a session or flushed
        if inspector is None or inspector.transient or inspector.pending:
            # Try to get attributes directly if not persistent, might fail if not set
            pk_vals = []
            mapper = class_mapper(self.__class__)
            pk_cols = mapper.primary_key
            if pk_cols:
                for col in pk_cols:
                    val = getattr(self, col.key, '(Not Set)')
                    pk_vals.append(f"{col.key}={val!r}")
            pk_str = ", ".join(pk_vals) + " (transient/pending)" if pk_vals else "(transient/pending)"

        else:
            # Object is persistent, get PK values reliably
            mapper = class_mapper(self.__class__)
            pk_cols = mapper.primary_key
            if pk_cols:
                 pk_vals = [f"{col.key}={getattr(self, col.key, 'N/A')!r}" for col in pk_cols]
                 pk_str = ", ".join(pk_vals)
            else:
                 pk_str = "(no primary key)"

        return f"<{self.__class__.__name__}({pk_str})>"

# Inherit from the Mixin and the SQLAlchemy base class
class Base(ReprMixin, DeclarativeBase):
    pass


# --- END - app/db/models/base.py ---