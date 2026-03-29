import re
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional, Annotated
# Python 3.10 compatibility ke liye ye zaroori hai
from typing_extensions import Self 
from pydantic import BaseModel, Field, StringConstraints, field_validator, model_validator

# --- YEH CLASS ADD KI GAYI HAI ---
class CategoryRequest(BaseModel):
    """Validate Product Categories"""
    name: Annotated[str, StringConstraints(min_length=2, max_length=50, strip_whitespace=True)]
    description: Optional[str] = Field(None, max_length=200)
    is_active: bool = Field(True)

    @field_validator('name')
    @classmethod
    def validate_category_name(cls, v: str) -> str:
        # Sirf alphanumeric aur spaces allow karne ke liye
        if not re.match(r'^[a-zA-Z0-9\s]+$', v):
            raise ValueError('Category name mein sirf letters, numbers aur spaces allowed hain')
        return v
# --------------------------------

# --- Ye Classes Add Karein ---

class CategoryRequest(BaseModel):
    """Validate Product Categories"""
    name: Annotated[str, StringConstraints(min_length=2, max_length=50, strip_whitespace=True)]
    description: Optional[str] = Field(None, max_length=200)

    @field_validator('name')
    @classmethod
    def validate_category_name(cls, v: str) -> str:
        if not re.match(r'^[a-zA-Z0-9\s]+$', v):
            raise ValueError('Category name mein sirf letters aur numbers allow hain')
        return v

class SearchQuery(BaseModel):
    """Validate Search Input"""
    query: Annotated[str, StringConstraints(min_length=1, max_length=100, strip_whitespace=True)]

    @field_validator('query')
    @classmethod
    def clean_query(cls, v: str) -> str:
        # SQL injection ya bad characters se bachne ke liye
        return re.sub(r'[^\w\s]', '', v)

# --- Baaki purana code niche rehne dein (PaymentRequest, etc.) ---
