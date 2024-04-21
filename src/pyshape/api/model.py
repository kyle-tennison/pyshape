"""Models for OnShape API payloads & responses"""

from enum import Enum
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional, Protocol


class NameIdFetchable(Protocol):
    name: str | None
    id: str | None


class ApiModel(BaseModel):

    model_config = ConfigDict(extra="ignore")


class UserReference(ApiModel):
    """Represents a reference to a user"""

    href: str
    id: str
    name: str


class Workspace(ApiModel):
    """Represents an instance of OnShape's workspace versioning"""

    name: str
    id: str


class Document(ApiModel):
    """Represents surface-level document information"""

    createdAt: datetime
    createdBy: UserReference
    href: str
    id: str
    name: str
    owner: UserReference
    defaultWorkspace: Workspace


class DocumentsResponse(ApiModel):
    """Response model of GET /documents"""

    items: list[Document]


class DocumentCreateRequest(ApiModel):
    """Request model of POST /documents"""

    name: str
    description: str | None
    isPublic: Optional[bool] = False


class Element(ApiModel):
    """Represents an OnShape element"""

    angleUnits: str | None
    areaUnits: str | None
    lengthUnits: str | None
    massUnits: str | None
    volumeUnits: str | None
    elementType: str
    id: str
    name: str


class FeatureParameter(ApiModel):
    """Represents a feature parameter"""
    btType: str
    queries: list[dict|ApiModel]
    parameterId: str

class FeatureParameterQueryList(FeatureParameter):
    """Represents a BTMParameterQueryList-148"""
    btType: str = "BTMParameterQueryList-148"

class FeatureEntity(ApiModel):
    """Represents a feature entity"""

    btType: Optional[str] = None
    entityId: str 

class SketchCurveEntity(FeatureEntity):
    """Represents a sketch's curve"""
    geometry: dict
    centerId: str

class Feature(ApiModel):
    """Represents an OnShape feature"""

    name: str
    namespace: str
    # nodeId: str
    featureType: str
    suppressed: bool
    parameters: Optional[list[FeatureParameter]] = []
    entities: Optional[list[FeatureEntity]]


class FeaturescriptUpload(ApiModel):
    """Request model of POST /partstudio/DWE/featurescript"""

    script: str


class FeaturescriptResponse(ApiModel):
    result: dict



class Sketch(Feature):
    """Represents a Sketch Feature"""

    btType: str = "BTMSketch-151"
    featureType: str = "featureType"
    constraints: Optional[list[dict]] = []