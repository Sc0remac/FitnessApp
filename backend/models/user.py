# # backend/models/user.py
# import uuid
# from datetime import datetime
# from sqlalchemy import Column, String, DateTime, Text # Text potentially for tokens if added
# from sqlalchemy.dialects.postgresql import UUID
# from sqlalchemy.orm import relationship
# from db.session import Base

# class User(Base):
#     # NOTE: This table might be minimal if most user data lives in auth.users
#     # or a separate 'profiles' table. It primarily serves to link auth ID
#     # for relationship definitions within SQLAlchemy if needed.
#     __tablename__ = "users" # Or potentially 'profiles' if you create that table instead

#     # This ID MUST match the ID in Supabase's auth.users table
#     id = Column(UUID(as_uuid=True), primary_key=True) # NOT default=uuid.uuid4() here! It comes from Supabase Auth.

#     # Store basic info potentially mirrored from auth for convenience or FKs
#     # Or leave these out if profiles table exists / using auth.users directly
#     email = Column(String, unique=True, index=True, nullable=False) # Mirror email from auth
#     full_name = Column(String, index=True, nullable=True) # Mirror full_name from auth metadata

#     # Timestamps for this specific record (if managing separate profile)
#     created_at = Column(DateTime(timezone=True), server_default='now()', nullable=False)
#     updated_at = Column(DateTime(timezone=True), server_default='now()', onupdate=datetime.utcnow, nullable=False)

#     # --- Spotify Tokens (Consider security implications) ---
#     # Option 1: Store here (less ideal for sensitive data unless encrypted)
#     # spotify_access_token = Column(Text, nullable=True) # Needs encryption at rest!
#     # spotify_refresh_token = Column(Text, nullable=True) # Needs encryption at rest!
#     # spotify_token_expires_at = Column(DateTime(timezone=True), nullable=True)

#     # Option 2: Create a separate 'profiles' table for this sensitive data
#     # Option 3: Use Supabase Vault for secure secret storage (Recommended)

#     # --- Relationships (Define how User links to other models) ---
#     # Ensure `back_populates` matches the definition in the other models (Workout, MoodEntry, SpotifyTrack)
#     workouts = relationship("Workout", back_populates="user", cascade="all, delete-orphan")
#     mood_entries = relationship("MoodEntry", back_populates="user", cascade="all, delete-orphan")
#     spotify_tracks = relationship("SpotifyTrack", back_populates="user", cascade="all, delete-orphan")

#     def __repr__(self):
#         return f"<User(id={self.id}, email='{self.email}')>"

# # --- IMPORTANT ---
# # If using this User model, you need corresponding logic in your auth router (`/signup`)
# # to create a row in this 'users' table when a new user signs up in Supabase Auth.
# # This is often done using Supabase Database Functions triggered by auth events,
# # or explicitly in your backend API after successful signup confirmation.
# # If this table ONLY holds relationships, it might only need the ID column.
# # Consider if a separate 'profiles' table linked 1-to-1 to auth.users.id is cleaner,
# # especially for storing mutable profile data or sensitive tokens.