# # backend/models/spotify.py
# import uuid
# from datetime import datetime
# from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, Float, Boolean # Added Float/Boolean
# from sqlalchemy.dialects.postgresql import UUID
# from sqlalchemy.orm import relationship
# from db.session import Base

# class SpotifyTrack(Base):
#     __tablename__ = "spotify_tracks" # Choose your table name

#     id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4) # Internal DB ID

#     # Link to the user
#     user_id = Column(UUID(as_uuid=True), nullable=False, index=True) # Linked via RLS/API logic

#     # Spotify specific identifiers and data
#     spotify_track_id = Column(String, nullable=False, index=True) # Spotify's own track ID
#     played_at = Column(DateTime(timezone=True), nullable=False, index=True) # Timestamp from Spotify history

#     # Track metadata (denormalized for easier querying/display)
#     track_name = Column(Text, nullable=True)
#     artist_name = Column(Text, nullable=True) # Could be primary artist, or comma-separated
#     album_name = Column(Text, nullable=True)
#     track_uri = Column(String, nullable=True) # e.g., "spotify:track:..."
#     duration_ms = Column(Integer, nullable=True)
#     explicit = Column(Boolean, nullable=True)
#     popularity = Column(Integer, nullable=True) # 0-100 scale from Spotify

#     # Optional: Store fetched audio features (consider performance/necessity)
#     # energy = Column(Float, nullable=True)
#     # valence = Column(Float, nullable=True)
#     # tempo = Column(Float, nullable=True)
#     # danceability = Column(Float, nullable=True)
#     # acousticness = Column(Float, nullable=True)
#     # instrumentalness = Column(Float, nullable=True)
#     # liveness = Column(Float, nullable=True)
#     # speechiness = Column(Float, nullable=True)
#     # mode = Column(Integer, nullable=True) # Major (1) or minor (0)
#     # time_signature = Column(Integer, nullable=True)

#     created_at = Column(DateTime(timezone=True), server_default='now()', nullable=False) # Record creation time in *our* DB

#     # --- Relationship (Optional) ---
#     # user = relationship("User", back_populates="spotify_tracks")

#     def __repr__(self):
#         return f"<SpotifyTrack(id={self.id}, user={self.user_id}, track='{self.track_name}', time='{self.played_at}')>"