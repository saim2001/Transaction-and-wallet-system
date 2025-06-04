import uuid
from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import text
from sqlalchemy.orm import joinedload,selectinload
from sqlalchemy.sql.elements import UnaryExpression
from schema.pagination_schema import PaginatedResponse,PaginatedRequest
from typing import Type, TypeVar, List, Any, Dict, Optional
from sqlalchemy.sql import func
from pydantic import BaseModel
from utils.utils import  get_utc_now

ModelType = TypeVar("ModelType")
ResponseType = TypeVar("ResponseType")

class BaseORM:
    def __init__(self, db: AsyncSession, model: Type[ModelType]):
        """
        Initialize the base class with a database session and a model.
        :param db: Async SQLAlchemy session
        :param model: SQLAlchemy ORM model class
        """
        self.db = db
        self.model = model

    async def create(self, obj_data: Dict[str, Any],commit: bool = True) -> ModelType:
        """
        Create a new record.
        :param obj_data: Dictionary of field values
        :return: Created model instance
        """
        if isinstance(obj_data, BaseModel):  # Check if obj_data is a Pydantic model
            obj_data = obj_data.dict()  # Convert to dictionary

        obj = self.model(**obj_data)
        self.db.add(obj)
        if commit:
            await self.db.commit()
        return obj

    async def create_many(self, obj_data: List[Dict[str, Any]],commit: bool = True) -> List[ModelType]:
        """
        Create multiple new records.
        :param obj_data: List of dictionaries of field values
        :return: List of created model instances
        """
        objs = [self.model(**data) for data in obj_data]
        self.db.add_all(objs)
        if commit:
            await self.db.commit()
            objs = [await self.db.refresh(obj) for obj in objs]
        return objs
    # async def update(self, obj_id: Any, obj_data: Dict[str, Any]) -> Optional[ModelType]:
    #     """
    #     Update a record by its ID.
    #     :param obj_id: ID of the record to update
    #     :param obj_data: Dictionary of updated field values
    #     :return: Updated model instance or None if not found
    #     """
    #     obj = await self.get_by_id(obj_id)
    #     if obj:
    #         for key, value in obj_data.items():
    #             setattr(obj, key, value)
    #         await self.db.commit()
    #         await self.db.refresh(obj)
    #     return obj

    async def update(self, obj: Any, commit: bool = True) -> Optional[ModelType]:
        """
        Update a record by its ID.
        :param obj_id: ID of the record to update
        :return: Updated model instance or None if not found
        """
        if obj.updated_at is None:
            obj.updated_at = get_utc_now()
        
        if commit:
            await self.db.commit()
            await self.db.refresh(obj)
        return obj

    async def delete(self, obj_id: Any,soft_delete: Optional[bool] = False,user_id: Optional[uuid.UUID] = None) -> bool:
        """
        Delete a record by its ID.
        :param obj_id: ID of the record to delete
        :return: True if the record was deleted, False otherwise
        """
        obj = await self.get_by_id(obj_id)
        if obj:
            if soft_delete == False:
                await self.db.delete(obj)
            else:
                obj.is_active = False
                obj.updated_at = get_utc_now()
                if user_id:
                    obj.updated_by = user_id
                else:
                    raise ValueError("user_id is required for soft delete")
                await self.db.commit()
                await self.db.refresh(obj)
                return obj
            await self.db.commit()
            return True
        return False

    async def get_by_id(self, obj_id: Any, relationships: Optional[List[str]] = None) -> Optional[ModelType]:
        """
        Get a record by its ID with optional relationships.
        :param obj_id: ID of the record
        :param relationships: List of relationships to load (eager loading)
        :return: Model instance or None if not found
        """
        query = select(self.model).filter(self.model.id == obj_id)
        if relationships:
            for rel in relationships:
                    attr = getattr(self.model, rel, None)
                    if attr is None:
                        raise ValueError(f"Relationship '{rel}' does not exist on model '{self.model.__name__}'.")
                    query = query.options(selectinload(attr))
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_all(
        self, 
        limit: Optional[int] = None, 
        offset: Optional[int] = None, 
        relationships: Optional[List[str]] = None
    ) -> List[ModelType]:
        """
        Get all records with optional relationships, limit, and offset.
        :param limit: Maximum number of records to return
        :param offset: Number of records to skip
        :param relationships: List of relationships to load (eager loading)
        :return: List of model instances
        """
        query = select(self.model)
        if relationships:
            for rel in relationships:
                query = query.options(joinedload(rel))
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def filter(
        self, 
        filters: List[Any], 
        relationships: Optional[List[str]] = None,
        order_by: Optional[List[Any]] = None
    ) -> List[ModelType]:
        """
        Apply filters and retrieve matching records with optional relationships.
        :param filters: List of SQLAlchemy filter conditions
        :param relationships: List of relationships to load (eager loading)
        :return: List of filtered model instances
        """
        query = select(self.model).filter(*filters)
        if order_by:
            for order_condition in order_by:
                if not isinstance(order_condition, UnaryExpression):
                    raise ValueError(f"Invalid order_by condition: {order_condition}")
                query = query.order_by(order_condition)
        if relationships:
            for rel in relationships:
                attr = getattr(self.model, rel, None)
                if attr is None:
                    raise ValueError(f"Relationship '{rel}' does not exist on model '{self.model.__name__}'.")
                query = query.options(joinedload(attr))
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_by_filter(
        self, 
        filters: List[Any], 
        relationships: Optional[List[str]] = None
    ) -> Optional[ModelType]:
        """
        Get the first record matching the filters with optional relationships.
        :param filters: List of SQLAlchemy filter conditions
        :param relationships: List of relationships to load (eager loading)
        :return: First matching model instance or None if not found
        """
        # Build the base query with filters
        query = select(self.model).filter(*filters)

        # Apply relationships if provided
        if relationships:
            for rel in relationships:
                print("self.model.__name__", rel)
                # Dynamically get the relationship attribute
                attr = getattr(self.model, rel, None)
                if attr is None:
                    raise ValueError(f"Relationship '{rel}' does not exist on model '{self.model.__name__}'.")
                query = query.options(joinedload(attr))

        # Execute the query and fetch the first result
        result = await self.db.execute(query)
        return result.scalars().first()
    
    async def get_all_pagination(
        self,
        pagination: PaginatedRequest,
        response_model: Type[ResponseType],
        filters: Optional[List[Any]] = None,  # List of SQLAlchemy filter conditions
        order_by: Optional[List[Any]] = None
    ) -> PaginatedResponse[ResponseType]:
        """
        Get all records with pagination and optional filters.
        :param pagination: PaginatedRequest object containing skip and limit.
        :param response_model: Pydantic model to map database results.
        :param filters: List of filter conditions (SQLAlchemy expressions).
        :return: PaginatedResponse object containing data and pagination details.
        """
        # Build the base query
        query = select(self.model)
        count_query = select(func.count(self.model.id))

        # Apply filters if provided
        if filters:
            query = query.where(*filters)
            count_query = count_query.where(*filters)


        # Apply ordering if provided
        if order_by:
            for order_condition in order_by:
                if not isinstance(order_condition, UnaryExpression):
                    raise ValueError(f"Invalid order_by condition: {order_condition}")
                query = query.order_by(order_condition)

        # Query for the total count of records
        count_result = await self.db.execute(count_query)
        total_count = count_result.scalar()

        # Query for paginated records
        data_query = await self.db.execute(
            query.offset(pagination.skip).limit(pagination.limit)
        )
        records = data_query.scalars().all()

        # Map records to the response model
        data = [response_model.from_orm(record) for record in records]

        # Calculate total pages
        total_pages = (total_count + pagination.limit - 1) // pagination.limit

        # Return paginated response
        return PaginatedResponse[ResponseType](
            page=(pagination.skip // pagination.limit) + 1,
            page_size=pagination.limit,
            total_count=total_count,
            total_pages=total_pages,
            data=data,
        )
    
    async def get_by_filter_with_pagination(
        self, 
        filters: List[Any], 
        pagination: PaginatedRequest,
        response_model: Type[ResponseType],
        relationships: Optional[List[str]] = None,
        joins: Optional[List[Any]] = None,
        order_by: Optional[List[Any]] = None
    ) -> PaginatedResponse[ResponseType]:
                
            """
            Get filtered records with pagination, optional relationships, and ordering.
            :param filters: List of SQLAlchemy filter conditions
            :param pagination: PaginatedRequest object containing skip and limit.
            :param response_model: Pydantic model to map database results.
            :param relationships: List of relationships to load (eager loading)
            :param order_by: List of columns or expressions to order by.
            :return: PaginatedResponse object containing data and pagination details.
            """
            # Build the base query with filters
            query = select(self.model).filter(*filters)
            count_query = select(func.count(self.model.id)).filter(*filters)

            # Apply relationships if provided
            if relationships:
                for rel in relationships:
                    # if  isinstance(rel,list):
                        
                    #     attr = getattr(self.model, rel[0], None)  # First level
                    #     nest_attr = getattr(attr, attr_parts[1], None)  # Second level
                    #     if attr is None:
                    #         raise ValueError(f"Relationship '{attr_parts[0]}' does not exist on model '{self.model.__name__}'.")
                    #     if nest_attr is None:
                    #         raise ValueError(f"Relationship '{attr_parts[1]}' does not exist on model '{self.model.__name__}'.")
                    #     query = query.options(joinedload(attr).joinedload(nest_attr))  # Load nested parts
                    # else:
                    attr = getattr(self.model, rel, None)
                    if attr is None:
                        raise ValueError(f"Relationship '{rel}' does not exist on model '{self.model.__name__}'.")
                    query = query.options(joinedload(attr))
          
            # Apply ordering if provided
            if order_by:
                for order_condition in order_by:
                    if not isinstance(order_condition, UnaryExpression):
                        raise ValueError(f"Invalid order_by condition: {order_condition}")
                    query = query.order_by(order_condition)

            # Query for the total count of records
            count_result = await self.db.execute(count_query)
            total_count = count_result.scalar()

            # Query for paginated records
            data_query = await self.db.execute(
                query.offset(pagination.skip).limit(pagination.limit)
            )
            records = data_query.unique().scalars().all()

            for record in records:
                print(record.__dict__)
            # Map records to the response model
            data = [response_model.from_orm(record) for record in records]

            # Calculate total pages
            total_pages = (total_count + pagination.limit - 1) // pagination.limit

            # Return paginated response
            return PaginatedResponse[ResponseType](
                page=(pagination.skip // pagination.limit) + 1,
                page_size=pagination.limit,
                total_count=total_count,
                total_pages=total_pages,
                data=data,
            )
    

    async def get_by_filter_custom_options(
        self, 
        filters: List[Any], 
        options: List[Any] = None,
    ) -> Optional[ModelType]:
        """
        Get the first record matching the filters with optional relationships.
        :param filters: List of SQLAlchemy filter conditions
        :param relationships: List of relationships to load (eager loading)
        :return: First matching model instance or None if not found
        """
        # Build the base query with filters
        query = select(self.model).filter(*filters)

        # Apply relationships if provided
        if options:
            query = query.options(*options)
        # Execute the query and fetch the first result
        result = await self.db.execute(query)
        return result.scalars().first()
    
    async def get_by_id_custom_options(
        self, 
        id: uuid.UUID, 
        options: List[Any] = None,
    ) -> Optional[ModelType]:
        """
        Get the first record matching the filters with optional relationships.
        :param filters: List of SQLAlchemy filter conditions
        :param relationships: List of relationships to load (eager loading)
        :return: First matching model instance or None if not found
        """
        # Build the base query with filters
        query = select(self.model).filter(self.model.id == id)

        # Apply relationships if provided
        if options:
            query = query.options(*options)
        # Execute the query and fetch the first result
        result = await self.db.execute(query)
        return result.scalars().first()
    
    async def get_by_filter_with_pagination_custom_options(
        self, 
        pagination: PaginatedRequest,
        response_model: Type[ResponseType],
        custom_query: Optional[Select] = None,
        count_column: Optional[Any] = None,
        options: Optional[List[Any]] = None,
        order_by: Optional[List[Any]] = None,
        filters: Optional[List[Any]] = None, 
    ) -> PaginatedResponse[ResponseType]:
                
            """
            Get filtered records with pagination, optional relationships, and ordering.
            :param filters: List of SQLAlchemy filter conditions
            :param pagination: PaginatedRequest object containing skip and limit.
            :param response_model: Pydantic model to map database results.
            :param relationships: List of relationships to load (eager loading)
            :param order_by: List of columns or expressions to order by.
            :return: PaginatedResponse object containing data and pagination details.
            """
            # Build the base query with filters
            query = custom_query if custom_query is not None else select(self.model).filter(*filters)
            if custom_query is not None and count_column is not None:
                count_query = select(func.count()).select_from(custom_query.subquery())
            else:
                count_query = select(func.count(self.model.id)).filter(*filters)

            if options:
                query = query.options(*options)

            print(options)

            # Apply ordering if provided
            if order_by:
                for order_condition in order_by:
                    if not isinstance(order_condition, UnaryExpression):
                        raise ValueError(f"Invalid order_by condition: {order_condition}")
                    query = query.order_by(order_condition)

            # Query for the total count of records
            count_result = await self.db.execute(count_query)
            total_count = count_result.scalar()

            # Query for paginated records
            data_query = await self.db.execute(
                query.offset(pagination.skip).limit(pagination.limit)
            )

            records = data_query.scalars().all() if custom_query is None else data_query.unique().fetchall()
            # Map records to the response model
            if custom_query is None:
                data = [response_model.from_orm(record) for record in records]
            else:
                data = [record._asdict() for record in records]

            # Calculate total pages
            total_pages = (total_count + pagination.limit - 1) // pagination.limit

            # Return paginated response
            return PaginatedResponse[ResponseType](
                page=(pagination.skip // pagination.limit) + 1,
                page_size=pagination.limit,
                total_count=total_count,
                total_pages=total_pages,
                data=data,
            )


    
        
    async def get_filter_items(
    self, 
    filters: List[Any], 
    relationships: Optional[List[str]] = None,
    distinct_columns: Optional[List[Any]] = None
    ) -> List[Any]:
        """
        Apply filters and retrieve matching records with optional relationships.
        Supports fetching distinct records based on specified columns.
        
        :param filters: List of SQLAlchemy filter conditions.
        :param relationships: List of relationships to load (eager loading).
        :param distinct_columns: List of columns to apply distinct on.
        :return: List of filtered model instances or tuples (if distinct_columns is provided).
        """
        # Build the query
        if distinct_columns:
            # Select specific columns and apply DISTINCT
            query = select(*distinct_columns).filter(*filters).distinct()
        else:
            # Select full model and apply filters
            query = select(self.model).filter(*filters)
            
            # Add relationships if provided
            if relationships:
                for rel in relationships:
                    query = query.options(joinedload(rel))

        # Execute the query
        result = await self.db.execute(query)

        # # Handle distinct results
        # if distinct_columns:
        #     # Fetch results as a list of tuples
        #     return result.scalars().all()  

        # Default: Fetch and return ORM instances
        return result.scalars().all()  
                


        
    



    