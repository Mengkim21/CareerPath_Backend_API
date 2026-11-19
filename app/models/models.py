import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Numeric, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.core.database import Base

# Users table
class User(Base):
  __tablename__ = "users"

  id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
  email = Column(String(255), unique=True, nullable=False)
  full_name = Column(String(255), nullable=False)
  created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

  # Relationship
  documents = relationship("Document", back_populates="user", cascade="all, delete-orphan")
  sessions = relationship("InterviewSession", back_populates="user", cascade="all, delete-orphan")

# Documents table (resumes / transcripts)
class Document(Base):
  __tablename__ = "documents"

  id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
  user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
  doc_type = Column(String(50), nullable=False)
  file_name = Column(String(255), nullable=False)
  raw_text = Column(Text, nullable=False)
  parsed_skills = Column(JSONB, default=list)
  parsed_coursework = Column(JSONB, default=list)
  gpa = Column(Numeric(3, 2), nullable=True)
  major = Column(String(255), nullable=True)
  ats_audit = Column(JSONB, default=dict)
  created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

  # Relationship
  user = relationship("User", back_populates="documents")
  matches = relationship("JobMatch", back_populates="document", cascade="all, delete-orphan")
  sessions = relationship("InterviewSession", back_populates="document")

# Job Roles table 
class JobRole(Base):
  __tablename__ = "job_roles"

  id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
  title = Column(String(255), nullable=False)
  industry = Column(String(100), nullable=False)
  company_type = Column(String(100), nullable=True)
  required_skills = Column(JSONB, nullable=False)
  learning_skills = Column(JSONB, default=list)
  full_description = Column(Text, nullable=True)
  created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

  # Relationship
  matches = relationship("JobMatch", back_populates="job_role")
  sessions = relationship("InterviewSession", back_populates="job_role")

# Job Matches table
class JobMatch(Base):
  __tablename__ = "job_matches"

  id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
  document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
  job_role_id = Column(UUID(as_uuid=True), ForeignKey("job_roles.id", ondelete="RESTRICT"), nullable=False)
  match_percentage = Column(Numeric(5, 2), nullable=False)
  missing_skills = Column(JSONB, default=list)
  created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

  # Relationships
  document = relationship("Document", back_populates="matches")
  job_role = relationship("JobRole", back_populates="matches")

# Interview Sessions table
class InterviewSession(Base):
  __tablename__ = "interview_sessions"

  id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
  user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
  document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="RESTRICT"), nullable=False)
  job_role_id = Column(UUID(as_uuid=True), ForeignKey("job_roles.id", ondelete="RESTRICT"), nullable=False)
  status = Column(String(50), default="IN_PROGRESS")

  # Rubric Scores (Charter Feature 5)
  final_score = Column(Numeric(5, 2), nullable=True)
  technical_score = Column(Numeric(5, 2), nullable=True)
  star_score = Column(Numeric(5, 2), nullable=True)
  fluency_score = Column(Numeric(5, 2), nullable=True)
  lexical_score = Column(Numeric(5, 2), nullable=True)
  
  feedback_en = Column(Text, nullable=True)
  feedback_km = Column(Text, nullable=True)

  started_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
  ended_at = Column(DateTime, nullable=True)

  # Relationships
  user = relationship("User", back_populates="sessions")
  document = relationship("Document", back_populates="sessions")
  job_role = relationship("JobRole", back_populates="sessions")
  turns = relationship("InterviewTurn", back_populates="session", cascade="all, delete-orphan")

# Interview Turns table
class InterviewTurn(Base):
  __tablename__ = "interview_turns"

  id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
  session_id = Column(UUID(as_uuid=True), ForeignKey("interview_sessions.id", ondelete="CASCADE"), nullable=False)
  turn_number = Column(Integer, nullable=False)
  question_text = Column(Text, nullable=False)
  user_transcript = Column(Text, nullable=False)
  
  # Real-Time Voice Metrics
  wpm = Column(Numeric(5, 2), nullable=True)
  filler_count = Column(Integer, default=0)
  
  # Post-Evaluation Metrics
  technical_score = Column(Numeric(5, 2), nullable=True)
  star_score = Column(Numeric(5, 2), nullable=True)
  turn_feedback = Column(Text, nullable=True)
  created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

  # Relationships
  session = relationship("InterviewSession", back_populates="turns")