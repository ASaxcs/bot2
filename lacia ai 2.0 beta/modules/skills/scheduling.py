"""
Scheduling Module untuk Lacia AI
Menangani penjadwalan, pengingat, dan manajemen waktu
"""

import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import time

class TaskStatus(Enum):
    """Status tugas"""
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    OVERDUE = "overdue"

class Priority(Enum):
    """Prioritas tugas"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4

class RecurrenceType(Enum):
    """Tipe pengulangan"""
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"
    CUSTOM = "custom"

@dataclass
class ScheduledTask:
    """Struktur tugas terjadwal"""
    id: str
    title: str
    description: str
    scheduled_time: datetime
    priority: Priority
    status: TaskStatus
    recurrence: RecurrenceType
    recurrence_interval: int = 1
    reminder_minutes: List[int] = None
    tags: List[str] = None
    metadata: Dict[str, Any] = None
    callback: Optional[str] = None
    created_at: datetime = None
    completed_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.reminder_minutes is None:
            self.reminder_minutes = [15, 5]  # Default 15 dan 5 menit sebelumnya
        if self.tags is None:
            self.tags = []
        if self.metadata is None:
            self.metadata = {}
        if self.created_at is None:
            self.created_at = datetime.now()

class Scheduler:
    """Sistem penjadwalan dan pengingat"""
    
    def __init__(self, data_file: str = "data/schedule.json"):
        self.data_file = data_file
        self.tasks: Dict[str, ScheduledTask] = {}
        self.callbacks: Dict[str, Callable] = {}
        self.running = False
        self.scheduler_thread = None
        self.load_tasks()
    
    def load_tasks(self):
        """Memuat tugas dari file"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for task_data in data:
                    task = ScheduledTask(**task_data)
                    # Convert string datetime back to datetime objects
                    task.scheduled_time = datetime.fromisoformat(task.scheduled_time)
                    task.created_at = datetime.fromisoformat(task.created_at)
                    if task.completed_at:
                        task.completed_at = datetime.fromisoformat(task.completed_at)
                    
                    self.tasks[task.id] = task
        except FileNotFoundError:
            self.tasks = {}
        except Exception as e:
            print(f"Error loading tasks: {e}")
            self.tasks = {}
    
    def save_tasks(self):
        """Menyimpan tugas ke file"""
        try:
            # Convert datetime objects to strings for JSON serialization
            serializable_tasks = []
            for task in self.tasks.values():
                task_dict = asdict(task)
                task_dict['scheduled_time'] = task.scheduled_time.isoformat()
                task_dict['created_at'] = task.created_at.isoformat()
                if task.completed_at:
                    task_dict['completed_at'] = task.completed_at.isoformat()
                # Remove callback function from serialization
                task_dict.pop('callback', None)
                serializable_tasks.append(task_dict)
            
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(serializable_tasks, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving tasks: {e}")
    
    def add_task(self, title: str, description: str, 
                scheduled_time: datetime, priority: Priority = Priority.MEDIUM,
                recurrence: RecurrenceType = RecurrenceType.NONE,
                recurrence_interval: int = 1,
                reminder_minutes: List[int] = None,
                tags: List[str] = None,
                callback: Optional[str] = None) -> str:
        """Menambah tugas baru"""
        
        task_id = f"task_{int(time.time())}_{len(self.tasks)}"
        
        task = ScheduledTask(
            id=task_id,
            title=title,
            description=description,
            scheduled_time=scheduled_time,
            priority=priority,
            status=TaskStatus.PENDING,
            recurrence=recurrence,
            recurrence_interval=recurrence_interval,
            reminder_minutes=reminder_minutes or [15, 5],
            tags=tags or [],
            callback=callback
        )
        
        self.tasks[task_id] = task
        self.save_tasks()
        
        return task_id
    
    def get_task(self, task_id: str) -> Optional[ScheduledTask]:
        """Mendapatkan tugas berdasarkan ID"""
        return self.tasks.get(task_id)
    
    def update_task(self, task_id: str, **kwargs) -> bool:
        """Update tugas"""
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        for key, value in kwargs.items():
            if hasattr(task, key):
                setattr(task, key, value)
        
        self.save_tasks()
        return True
    
    def delete_task(self, task_id: str) -> bool:
        """Hapus tugas"""
        if task_id in self.tasks:
            del self.tasks[task_id]
            self.save_tasks()
            return True
        return False
    
    def complete_task(self, task_id: str) -> bool:
        """Tandai tugas sebagai selesai"""
        if task_id in self.tasks:
            self.tasks[task_id].status = TaskStatus.COMPLETED
            self.tasks[task_id].completed_at = datetime.now()
            
            # Jika ada recurrence, buat tugas berikutnya
            if self.tasks[task_id].recurrence != RecurrenceType.NONE:
                self._create_recurring_task(self.tasks[task_id])
            
            self.save_tasks()
            return True
        return False
    
    def _create_recurring_task(self, original_task: ScheduledTask):
        """Buat tugas berulang berikutnya"""
        next_time = self._calculate_next_occurrence(
            original_task.scheduled_time, 
            original_task.recurrence, 
            original_task.recurrence_interval
        )
        
        if next_time:
            self.add_task(
                title=original_task.title,
                description=original_task.description,
                scheduled_time=next_time,
                priority=original_task.priority,
                recurrence=original_task.recurrence,
                recurrence_interval=original_task.recurrence_interval,
                reminder_minutes=original_task.reminder_minutes,
                tags=original_task.tags,
                callback=original_task.callback
            )
    
    def _calculate_next_occurrence(self, current_time: datetime, 
                                 recurrence: RecurrenceType, 
                                 interval: int) -> Optional[datetime]:
        """Hitung waktu occurrence berikutnya"""
        if recurrence == RecurrenceType.DAILY:
            return current_time + timedelta(days=interval)
        elif recurrence == RecurrenceType.WEEKLY:
            return current_time + timedelta(weeks=interval)
        elif recurrence == RecurrenceType.MONTHLY:
            # Approximate monthly (30 days)
            return current_time + timedelta(days=30 * interval)
        elif recurrence == RecurrenceType.YEARLY:
            # Approximate yearly (365 days)
            return current_time + timedelta(days=365 * interval)
        
        return None
    
    def get_tasks_by_date(self, date: datetime) -> List[ScheduledTask]:
        """Dapatkan tugas berdasarkan tanggal"""
        target_date = date.date()
        return [
            task for task in self.tasks.values()
            if task.scheduled_time.date() == target_date
        ]
    
    def get_upcoming_tasks(self, hours_ahead: int = 24) -> List[ScheduledTask]:
        """Dapatkan tugas yang akan datang"""
        now = datetime.now()
        cutoff = now + timedelta(hours=hours_ahead)
        
        upcoming = [
            task for task in self.tasks.values()
            if now <= task.scheduled_time <= cutoff and task.status == TaskStatus.PENDING
        ]
        
        return sorted(upcoming, key=lambda x: x.scheduled_time)
    
    def get_overdue_tasks(self) -> List[ScheduledTask]:
        """Dapatkan tugas yang terlambat"""
        now = datetime.now()
        overdue = [
            task for task in self.tasks.values()
            if task.scheduled_time < now and task.status == TaskStatus.PENDING
        ]
        
        # Update status ke overdue
        for task in overdue:
            task.status = TaskStatus.OVERDUE
        
        if overdue:
            self.save_tasks()
        
        return overdue
    
    def get_tasks_by_priority(self, priority: Priority) -> List[ScheduledTask]:
        """Dapatkan tugas berdasarkan prioritas"""
        return [
            task for task in self.tasks.values()
            if task.priority == priority
        ]
    
    def get_tasks_by_tag(self, tag: str) -> List[ScheduledTask]:
        """Dapatkan tugas berdasarkan tag"""
        return [
            task for task in self.tasks.values()
            if tag in task.tags
        ]
    
    def search_tasks(self, query: str) -> List[ScheduledTask]:
        """Cari tugas berdasarkan kata kunci"""
        query_lower = query.lower()
        results = []
        
        for task in self.tasks.values():
            if (query_lower in task.title.lower() or 
                query_lower in task.description.lower() or
                any(query_lower in tag.lower() for tag in task.tags)):
                results.append(task)
        
        return results
    
    def register_callback(self, name: str, callback: Callable):
        """Daftarkan callback function"""
        self.callbacks[name] = callback
    
    def start_scheduler(self):
        """Mulai scheduler daemon"""
        if self.running:
            return False
        
        self.running = True
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        return True
    
    def stop_scheduler(self):
        """Hentikan scheduler"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
    
    def _scheduler_loop(self):
        """Loop utama scheduler"""
        while self.running:
            try:
                self._check_tasks()
                time.sleep(60)  # Check setiap menit
            except Exception as e:
                print(f"Scheduler error: {e}")
                time.sleep(60)
    
    def _check_tasks(self):
        """Periksa tugas yang perlu dieksekusi atau diingatkan"""
        now = datetime.now()
        
        for task in list(self.tasks.values()):
            if task.status != TaskStatus.PENDING:
                continue
            
            # Cek reminder
            for reminder_min in task.reminder_minutes:
                reminder_time = task.scheduled_time - timedelta(minutes=reminder_min)
                if (now >= reminder_time and 
                    now < reminder_time + timedelta(minutes=1)):  # 1 menit tolerance
                    self._send_reminder(task, reminder_min)
            
            # Cek eksekusi tugas
            if now >= task.scheduled_time:
                self._execute_task(task)
    
    def _send_reminder(self, task: ScheduledTask, minutes_before: int):
        """Kirim pengingat"""
        print(f"⏰ REMINDER: '{task.title}' in {minutes_before} minutes")
        
        if task.callback and task.callback in self.callbacks:
            try:
                self.callbacks[task.callback]({
                    'type': 'reminder',
                    'task': task,
                    'minutes_before': minutes_before
                })
            except Exception as e:
                print(f"Callback error: {e}")
    
    def _execute_task(self, task: ScheduledTask):
        """Eksekusi tugas"""
        print(f"🔔 TASK DUE: '{task.title}' - {task.description}")
        
        task.status = TaskStatus.ACTIVE
        
        if task.callback and task.callback in self.callbacks:
            try:
                self.callbacks[task.callback]({
                    'type': 'execution',
                    'task': task
                })
            except Exception as e:
                print(f"Task execution error: {e}")
        
        self.save_tasks()
    
    def get_schedule_summary(self, days_ahead: int = 7) -> Dict[str, Any]:
        """Dapatkan ringkasan jadwal"""
        now = datetime.now()
        cutoff = now + timedelta(days=days_ahead)
        
        upcoming = [
            task for task in self.tasks.values()
            if now <= task.scheduled_time <= cutoff and task.status == TaskStatus.PENDING
        ]
        
        overdue = self.get_overdue_tasks()
        
        by_priority = {
            'urgent': len([t for t in upcoming if t.priority == Priority.URGENT]),
            'high': len([t for t in upcoming if t.priority == Priority.HIGH]),
            'medium': len([t for t in upcoming if t.priority == Priority.MEDIUM]),
            'low': len([t for t in upcoming if t.priority == Priority.LOW])
        }
        
        by_date = {}
        for task in upcoming:
            date_str = task.scheduled_time.date().isoformat()
            if date_str not in by_date:
                by_date[date_str] = []
            by_date[date_str].append({
                'id': task.id,
                'title': task.title,
                'time': task.scheduled_time.strftime('%H:%M'),
                'priority': task.priority.name
            })
        
        return {
            'total_upcoming': len(upcoming),
            'total_overdue': len(overdue),
            'by_priority': by_priority,
            'by_date': by_date,
            'next_task': upcoming[0].__dict__ if upcoming else None
        }
    
    def export_schedule(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Export jadwal dalam rentang tanggal"""
        tasks_in_range = [
            task for task in self.tasks.values()
            if start_date <= task.scheduled_time <= end_date
        ]
        
        return {
            'export_date': datetime.now().isoformat(),
            'date_range': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'total_tasks': len(tasks_in_range),
            'tasks': [asdict(task) for task in tasks_in_range]
        }