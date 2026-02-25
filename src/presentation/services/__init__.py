"""
BioRemPP Web - Presentation Services
====================================

Service layer for presentation logic.
"""

from .data_processing_service import DataProcessingService
from .job_resume_service import JobResumeService, job_resume_service

__all__ = ["DataProcessingService", "JobResumeService", "job_resume_service"]
