from typing import List, Dict, Optional


class PostModel:
    def __init__(self,
                page_name: str,
                text: str,
                images: Optional[List[str]] = None,
                comments: Optional[int] = None,
                shares: Optional[int] = None):
        self.page_name = page_name.strip() if page_name else None
        self.text = text.strip() if text else None
        self.images = images if images else []
        self.comments = comments
        self.shares = shares

    def is_valid(self) -> bool:
        """Vérifie si le post est complet et prêt à être inséré."""
        return bool(self.page_name and self.text)

    def to_dict(self) -> Dict:
        """Retourne un dictionnaire compatible MongoDB."""
        return {
            "page_name": self.page_name,
            "text": self.text,
            "images": self.images,
            "comments": self.comments,
            "shares": self.shares
        }
        
    def __repr__(self):
        return (
            f"PostModel(\n"
            f"  page_name={self.page_name!r},\n"
            f"  text={self.text!r},\n"
            f"  images={self.images!r},\n"
            f"  comments={self.comments!r},\n"
            f"  shares={self.shares!r}\n"
            f")"
        )