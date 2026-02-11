"""
Task service for business logic operations.
"""
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.task import Task, TaskStatus, TaskPriority
from app.models.user import User
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from app.repositories.task import TaskRepository
from app.repositories.user import UserRepository
from app.core.exceptions import NotFoundError, ConflictError, ValidationError

# Define constants for repeated literals
ONLY_UPDATE_OWN_TASKS = "You can only update your own tasks"
ONLY_DELETE_OWN_TASKS = "You can only delete your own tasks"
ONLY_ASSIGN_OWN_TASKS = "You can only assign your own tasks"


class TaskService:
    """
    Task service for task management operations.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.task_repo = TaskRepository(db)
        self.user_repo = UserRepository(db)
    
    def get_task_by_id(self, task_id: UUID) -> Task:
        """Get a task by ID."""
        task = self.task_repo.get(task_id)
        if not task:
            raise NotFoundError(f"Task with id {task_id} not found")
        return task
    
    def create_task(self, task_data: TaskCreate, owner_id: UUID) -> Task:
        """Create a new task for a user."""
        # Verify that the owner exists
        owner = self.user_repo.get(owner_id)
        if not owner:
            raise NotFoundError(f"User with id {owner_id} not found")
        
        if not owner.is_active:
            raise ValidationError("Cannot create task for inactive user")
        
        # Add owner_id to task data
        task_dict = task_data.model_dump()
        task_dict["owner_id"] = owner_id
        
        # Create task with updated data
        task_create = TaskCreate(**task_dict)
        return self.task_repo.create(task_create)
    
    def get_user_tasks(
        self, 
        owner_id: UUID, 
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Task]:
        """Get tasks for a specific user with optional filtering."""
        # Verify user exists
        user = self.user_repo.get(owner_id)
        if not user:
            raise NotFoundError(f"User with id {owner_id} not found")
        
        if status:
            return self.task_repo.get_by_status(status, owner_id, skip, limit)
        elif priority:
            return self.task_repo.get_by_priority(priority, owner_id, skip, limit)
        else:
            return self.task_repo.get_by_owner(owner_id, skip, limit)
    
    def update_task(self, task_id: UUID, task_update: TaskUpdate, owner_id: Optional[UUID] = None) -> Task:
        """Update a task."""
        task = self.task_repo.get(task_id)
        if not task:
            raise NotFoundError(f"Task with id {task_id} not found")
        
        # If owner_id is provided, verify ownership
        if owner_id and task.owner_id != owner_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=ONLY_UPDATE_OWN_TASKS
            )
        
        return self.task_repo.update(task, task_update)
    
    def delete_task(self, task_id: UUID, owner_id: Optional[UUID] = None) -> Task:
        """Delete a task (soft delete)."""
        task = self.task_repo.get(task_id)
        if not task:
            raise NotFoundError(f"Task with id {task_id} not found")
        
        # If owner_id is provided, verify ownership
        if owner_id and task.owner_id != owner_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=ONLY_DELETE_OWN_TASKS
            )
        
        return self.task_repo.soft_delete(task_id)
    
    def mark_task_completed(self, task_id: UUID, owner_id: Optional[UUID] = None) -> Task:
        """Mark a task as completed."""
        task = self.task_repo.get(task_id)
        if not task:
            raise NotFoundError(f"Task with id {task_id} not found")
        
        if owner_id and task.owner_id != owner_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=ONLY_UPDATE_OWN_TASKS
            )
        
        if task.status == TaskStatus.COMPLETED:
            raise ValidationError("Task is already completed")
        
        return self.task_repo.mark_completed(task_id)
    
    def mark_task_in_progress(self, task_id: UUID, owner_id: Optional[UUID] = None) -> Task:
        """Mark a task as in progress."""
        task = self.task_repo.get(task_id)
        if not task:
            raise NotFoundError(f"Task with id {task_id} not found")
        
        if owner_id and task.owner_id != owner_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=ONLY_UPDATE_OWN_TASKS
            )
        
        if task.status == TaskStatus.COMPLETED:
            raise ValidationError("Cannot change status of completed task")
        
        return self.task_repo.mark_in_progress(task_id)
    
    def mark_task_cancelled(self, task_id: UUID, owner_id: Optional[UUID] = None) -> Task:
        """Mark a task as cancelled."""
        task = self.task_repo.get(task_id)
        if not task:
            raise NotFoundError(f"Task with id {task_id} not found")
        
        if owner_id and task.owner_id != owner_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=ONLY_UPDATE_OWN_TASKS
            )
        
        if task.status == TaskStatus.COMPLETED:
            raise ValidationError("Cannot cancel completed task")
        
        return self.task_repo.mark_cancelled(task_id)
    
    def get_overdue_tasks(self, owner_id: Optional[UUID] = None, skip: int = 0, limit: int = 100) -> List[Task]:
        """Get overdue tasks."""
        if owner_id:
            # Verify user exists
            user = self.user_repo.get(owner_id)
            if not user:
                raise NotFoundError(f"User with id {owner_id} not found")
        
        return self.task_repo.get_overdue_tasks(owner_id, skip, limit)
    
    def get_upcoming_tasks(
        self, 
        days_ahead: int = 7,
        owner_id: Optional[UUID] = None, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Task]:
        """Get upcoming tasks."""
        if owner_id:
            # Verify user exists
            user = self.user_repo.get(owner_id)
            if not user:
                raise NotFoundError(f"User with id {owner_id} not found")
        
        return self.task_repo.get_upcoming_tasks(days_ahead, owner_id, skip, limit)
    
    def search_tasks(
        self, 
        search_term: str,
        owner_id: Optional[UUID] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Task]:
        """Search tasks by title or description."""
        if owner_id:
            # Verify user exists
            user = self.user_repo.get(owner_id)
            if not user:
                raise NotFoundError(f"User with id {owner_id} not found")
        
        return self.task_repo.search_tasks(search_term, owner_id, skip, limit)
    
    def get_task_statistics(self, owner_id: Optional[UUID] = None) -> Dict[str, Any]:
        """Get task statistics."""
        if owner_id:
            # Verify user exists
            user = self.user_repo.get(owner_id)
            if not user:
                raise NotFoundError(f"User with id {owner_id} not found")
        
        return self.task_repo.get_task_statistics(owner_id)
    
    def get_user_productivity_report(self, owner_id: UUID, days: int = 30) -> Dict[str, Any]:
        """Get user productivity report for the last N days."""
        user = self.user_repo.get(owner_id)
        if not user:
            raise NotFoundError(f"User with id {owner_id} not found")
        
        # Get tasks created in the time period
        from datetime import timezone
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        # Get all user tasks
        all_tasks = self.task_repo.get_by_owner(owner_id, skip=0, limit=1000)  # Get all tasks
        
        # Filter tasks by date
        period_tasks = [
            task for task in all_tasks 
            if task.created_at >= cutoff_date
        ]
        
        completed_tasks = [
            task for task in period_tasks 
            if task.status == TaskStatus.COMPLETED
        ]
        
        overdue_tasks = [
            task for task in period_tasks
            if task.due_date and task.due_date < datetime.now(timezone.utc)
            and task.status not in [TaskStatus.COMPLETED, TaskStatus.CANCELLED]
        ]
        
        # Calculate productivity metrics
        total_tasks = len(period_tasks)
        completed_count = len(completed_tasks)
        overdue_count = len(overdue_tasks)
        completion_rate = (completed_count / total_tasks * 100) if total_tasks > 0 else 0
        
        # Tasks by priority
        priority_distribution = {}
        for priority in TaskPriority:
            priority_distribution[priority.value] = len([
                task for task in period_tasks 
                if task.priority == priority
            ])
        
        # Tasks by status
        status_distribution = {}
        for status in TaskStatus:
            status_distribution[status.value] = len([
                task for task in period_tasks 
                if task.status == status
            ])
        
        return {
            "period_days": days,
            "total_tasks": total_tasks,
            "completed_tasks": completed_count,
            "overdue_tasks": overdue_count,
            "completion_rate": round(completion_rate, 2),
            "priority_distribution": priority_distribution,
            "status_distribution": status_distribution,
            "avg_tasks_per_day": round(total_tasks / days, 2) if days > 0 else 0
        }
    
    def bulk_update_status(
        self, 
        task_ids: List[UUID], 
        new_status: TaskStatus,
        owner_id: Optional[UUID] = None
    ) -> List[Task]:
        """Bulk update status for multiple tasks."""
        updated_tasks = []
        
        for task_id in task_ids:
            try:
                task = self.task_repo.get(task_id)
                if not task:
                    continue
                
                # Check ownership if owner_id provided
                if owner_id and task.owner_id != owner_id:
                    continue
                
                updated_task = self.task_repo.update_status(task_id, new_status)
                if updated_task:
                    updated_tasks.append(updated_task)
                    
            except Exception:
                # Skip failed updates and continue with others
                continue
        
        return updated_tasks
    
    def assign_task(self, task_id: UUID, new_owner_id: UUID, current_owner_id: Optional[UUID] = None) -> Task:
        """Assign a task to a different user."""
        task = self.task_repo.get(task_id)
        if not task:
            raise NotFoundError(f"Task with id {task_id} not found")
        
        # Check if current user owns the task
        if current_owner_id and task.owner_id != current_owner_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=ONLY_ASSIGN_OWN_TASKS
            )
        
        # Verify new owner exists
        new_owner = self.user_repo.get(new_owner_id)
        if not new_owner:
            raise NotFoundError(f"User with id {new_owner_id} not found")
        
        if not new_owner.is_active:
            raise ValidationError("Cannot assign task to inactive user")
        
        # Update task owner
        task_update = TaskUpdate(owner_id=new_owner_id)
        return self.task_repo.update(task, task_update)
