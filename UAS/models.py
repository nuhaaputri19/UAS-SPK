from sqlalchemy import Float
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class restoran(Base):
    __tablename__ = 'restoran'
    id_restoran: Mapped[str] = mapped_column(primary_key=True)
    rating_makanan: Mapped[Float] = mapped_column(type_=Float)
    harga: Mapped[int] = mapped_column()
    kualitas_pelayanan: Mapped[Float] = mapped_column(type_=Float)
    suasana: Mapped[Float] = mapped_column(type_=Float)
    lokasi: Mapped[Float] = mapped_column(type_=Float)  
    
    def __repr__(self) -> str:
        return f"restoran(id_restoran={self.id_restoran!r}, harga={self.harga!r})"
