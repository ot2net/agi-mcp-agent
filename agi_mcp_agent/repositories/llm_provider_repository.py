"""Repository for managing LLM providers and model configurations."""

import logging
from typing import Any, Dict, List, Optional, Union, Tuple

from sqlalchemy import create_engine, or_
from sqlalchemy.orm import sessionmaker, Session

from agi_mcp_agent.models.llm_provider import (
    LLMProviderModel, 
    LLMProviderSettingModel, 
    LLMModelModel,
    get_default_providers,
    get_default_provider_settings,
    Base
)

logger = logging.getLogger(__name__)


class LLMProviderRepository:
    """Repository for managing LLM providers and models."""
    
    def __init__(self, db_url: str):
        """Initialize the repository.
        
        Args:
            db_url: Database connection URL
        """
        self.engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)
        
    def create_tables(self):
        """Create all tables if they don't exist."""
        Base.metadata.create_all(self.engine)
        logger.info("Created LLM provider database tables")
        
    def initialize_default_data(self):
        """Initialize database with default providers and settings."""
        session = self.Session()
        try:
            # Create default providers if needed
            providers = get_default_providers()
            for provider_data in providers:
                name = provider_data.pop("name")
                existing = session.query(LLMProviderModel).filter_by(name=name).first()
                
                if not existing:
                    provider = LLMProviderModel(name=name, **provider_data)
                    session.add(provider)
                    logger.info(f"Added default provider: {name}")
                
            session.commit()
            
            # Create provider settings
            settings = get_default_provider_settings()
            for setting_data in settings:
                provider_name = setting_data.pop("provider_name")
                provider = session.query(LLMProviderModel).filter_by(name=provider_name).first()
                
                if provider:
                    key = setting_data["key"]
                    existing = session.query(LLMProviderSettingModel).filter_by(
                        provider_id=provider.id, key=key
                    ).first()
                    
                    if not existing:
                        setting = LLMProviderSettingModel(provider_id=provider.id, **setting_data)
                        session.add(setting)
                        logger.info(f"Added default setting {key} for provider {provider_name}")
            
            session.commit()
            logger.info("Initialized default LLM provider data")
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error initializing default data: {str(e)}")
        finally:
            session.close()
            
    def get_all_providers(self, region: Optional[str] = None) -> List[LLMProviderModel]:
        """Get all providers.
        
        Args:
            region: Optional region filter
            
        Returns:
            List of provider models
        """
        session = self.Session()
        try:
            query = session.query(LLMProviderModel)
            if region:
                query = query.filter_by(region=region)
            return query.all()
        finally:
            session.close()
            
    def get_enabled_providers(self, region: Optional[str] = None) -> List[LLMProviderModel]:
        """Get enabled providers.
        
        Args:
            region: Optional region filter
            
        Returns:
            List of enabled provider models
        """
        session = self.Session()
        try:
            query = session.query(LLMProviderModel).filter_by(is_enabled=True)
            if region:
                query = query.filter_by(region=region)
            return query.all()
        finally:
            session.close()
            
    def get_provider_by_name(self, name: str) -> Optional[LLMProviderModel]:
        """Get a provider by name.
        
        Args:
            name: Provider name
            
        Returns:
            Provider model or None if not found
        """
        session = self.Session()
        try:
            return session.query(LLMProviderModel).filter_by(name=name).first()
        finally:
            session.close()
            
    def get_provider_settings(self, provider_id: int) -> List[LLMProviderSettingModel]:
        """Get settings for a provider.
        
        Args:
            provider_id: Provider ID
            
        Returns:
            List of provider setting models
        """
        session = self.Session()
        try:
            return session.query(LLMProviderSettingModel).filter_by(provider_id=provider_id).all()
        finally:
            session.close()
            
    def get_provider_setting(self, provider_id: int, key: str) -> Optional[LLMProviderSettingModel]:
        """Get a specific setting for a provider.
        
        Args:
            provider_id: Provider ID
            key: Setting key
            
        Returns:
            Provider setting model or None if not found
        """
        session = self.Session()
        try:
            return session.query(LLMProviderSettingModel).filter_by(provider_id=provider_id, key=key).first()
        finally:
            session.close()
            
    def update_provider_setting(self, provider_id: int, key: str, value: str) -> bool:
        """Update a provider setting.
        
        Args:
            provider_id: Provider ID
            key: Setting key
            value: Setting value
            
        Returns:
            Whether the update was successful
        """
        session = self.Session()
        try:
            setting = session.query(LLMProviderSettingModel).filter_by(provider_id=provider_id, key=key).first()
            if setting:
                setting.value = value
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"Error updating provider setting: {str(e)}")
            return False
        finally:
            session.close()
            
    def get_provider_settings_dict(self, provider_id: int) -> Dict[str, str]:
        """Get provider settings as a dictionary.
        
        Args:
            provider_id: Provider ID
            
        Returns:
            Dictionary of settings
        """
        settings = self.get_provider_settings(provider_id)
        return {s.key: s.value for s in settings if s.value is not None}
    
    def add_model(self, model: LLMModelModel) -> bool:
        """Add a model to the database.
        
        Args:
            model: Model to add
            
        Returns:
            Whether the operation was successful
        """
        session = self.Session()
        try:
            session.add(model)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"Error adding model: {str(e)}")
            return False
        finally:
            session.close()
            
    def update_model(self, model_id: int, **kwargs) -> bool:
        """Update a model.
        
        Args:
            model_id: Model ID
            **kwargs: Fields to update
            
        Returns:
            Whether the update was successful
        """
        session = self.Session()
        try:
            model = session.query(LLMModelModel).filter_by(id=model_id).first()
            if model:
                for key, value in kwargs.items():
                    if hasattr(model, key):
                        setattr(model, key, value)
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"Error updating model: {str(e)}")
            return False
        finally:
            session.close()
            
    def get_model_by_name(self, provider_id: int, name: str) -> Optional[LLMModelModel]:
        """Get a model by name.
        
        Args:
            provider_id: Provider ID
            name: Model name
            
        Returns:
            Model or None if not found
        """
        session = self.Session()
        try:
            return session.query(LLMModelModel).filter_by(provider_id=provider_id, name=name).first()
        finally:
            session.close()
            
    def get_model_by_id(self, model_id: int) -> Optional[LLMModelModel]:
        """Get a model by ID.
        
        Args:
            model_id: Model ID
            
        Returns:
            Model or None if not found
        """
        session = self.Session()
        try:
            return session.query(LLMModelModel).filter_by(id=model_id).first()
        finally:
            session.close()
            
    def get_models_by_provider(self, provider_id: int, enabled_only: bool = False) -> List[LLMModelModel]:
        """Get models for a provider.
        
        Args:
            provider_id: Provider ID
            enabled_only: Whether to get only enabled models
            
        Returns:
            List of models
        """
        session = self.Session()
        try:
            query = session.query(LLMModelModel).filter_by(provider_id=provider_id)
            if enabled_only:
                query = query.filter_by(is_enabled=True)
            return query.all()
        finally:
            session.close()
            
    def get_models_by_capability(self, capability: str) -> List[LLMModelModel]:
        """Get models that support a specific capability.
        
        Args:
            capability: Capability name
            
        Returns:
            List of models
        """
        # Note: This implementation assumes capabilities are stored in the 
        # JSON "capabilities" field as a list of strings or objects with a "name" field
        session = self.Session()
        try:
            # This is a simplification - actual JSON querying depends on the database
            # In production, you would use a proper JSON query based on your database
            models = session.query(LLMModelModel).filter(LLMModelModel.is_enabled == True).all()
            
            # Filter in Python (not ideal, but works across databases)
            result = []
            for model in models:
                if model.capabilities:
                    if isinstance(model.capabilities, list):
                        if capability in model.capabilities:
                            result.append(model)
                    elif isinstance(model.capabilities, dict):
                        if capability in model.capabilities.get("names", []):
                            result.append(model)
            
            return result
        finally:
            session.close()
            
    def get_all_models(self, enabled_only: bool = False) -> List[LLMModelModel]:
        """Get all models.
        
        Args:
            enabled_only: Whether to get only enabled models
            
        Returns:
            List of models
        """
        session = self.Session()
        try:
            query = session.query(LLMModelModel)
            if enabled_only:
                query = query.filter_by(is_enabled=True)
            return query.all()
        finally:
            session.close()
    
    def search_models(self, query: str, enabled_only: bool = True) -> List[LLMModelModel]:
        """Search for models by name or description.
        
        Args:
            query: Search query
            enabled_only: Whether to get only enabled models
            
        Returns:
            List of matching models
        """
        session = self.Session()
        try:
            search = f"%{query}%"
            db_query = session.query(LLMModelModel).filter(
                or_(
                    LLMModelModel.name.ilike(search),
                    LLMModelModel.display_name.ilike(search),
                    LLMModelModel.description.ilike(search)
                )
            )
            
            if enabled_only:
                db_query = db_query.filter_by(is_enabled=True)
                
            return db_query.all()
        finally:
            session.close() 