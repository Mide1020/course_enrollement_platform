from sqlalchemy.orm import Session
from app.models.module import Module
from app.schema.module import ModuleCreate, ModuleUpdate
import uuid


class CRUDModule:

    def create(self, db: Session, module: ModuleCreate):
        db_module = Module(
            title=module.title,
            order=module.order,
            course_id=module.course_id
        )
        db.add(db_module)
        return db_module

    def get_by_id(self, db: Session, module_id: uuid.UUID):
        return db.query(Module).filter(Module.id == module_id).first()
    
    def get_by_course(self, db: Session, course_id: uuid.UUID):
        return db.query(Module).filter(Module.course_id == course_id).order_by(Module.order).all()

    def update(self, db: Session, module_id: uuid.UUID, module_update: ModuleUpdate):
        db_module = self.get_by_id(db, module_id)
        if not db_module:
            return None
        
        update_data = module_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_module, field, value)
        
        return db_module
    
    def delete(self, db: Session, module_id: uuid.UUID):
        db_module = self.get_by_id(db, module_id)
        if not db_module:
            return None
        
        db.delete(db_module)
        return db_module


module_crud = CRUDModule()
