"""Various entities that might appear in a sketch"""

from enum import Enum
import math
from typing import TYPE_CHECKING, Self, override

import numpy as np
from onpy.features.entities.base import Entity
import onpy.api.model as model
from onpy.util.misc import UnitSystem, Point2D

if TYPE_CHECKING:
    from onpy.features import Sketch

class SketchCircle(Entity):

    def __init__(
        self,
        sketch: "Sketch",
        radius: float,
        center: Point2D,
        units: UnitSystem,
        dir: tuple[float, float] = (1, 0),
        clockwise: bool = False,
    ):

        self._sketch = sketch
        self.radius = radius
        self.center = center
        self.units = units
        self.dir = Point2D.from_pair(dir)
        self.clockwise = clockwise
        self.entity_id = self.generate_entity_id()

    @override
    def to_model(self) -> model.SketchCurveEntity:

        return model.SketchCurveEntity(
            geometry={
                "btType": "BTCurveGeometryCircle-115",
                "radius": self.radius,
                "xcenter": self.center.x,
                "ycenter": self.center.y,
                "xdir": self.dir.x,
                "ydir": self.dir.y,
                "clockwise": self.clockwise,
            },
            centerId=f"{self.entity_id}.center",
            entityId=f"{self.entity_id}",
        )
    
    @property
    @override
    def _feature(self) -> "Sketch":
        return self._sketch
    
    @override
    def rotate(self, origin: tuple[float, float], theta: float):
        new_center = self._rotate_point(self.center, Point2D.from_pair(origin), theta)
        new_entity = SketchCircle(
            sketch=self._feature,
            radius=self.radius,
            center=new_center,
            units=self.units,
            dir=self.dir.as_tuple,
            clockwise=self.clockwise
        )
        self._replace_entity(new_entity)
        return new_entity

    
    @override
    def translate(self, x:float, y: float):

        new_center = Point2D(self.center.x + x, self.center.y + y)
        new_entity = SketchCircle(
            sketch=self._feature,
            radius=self.radius,
            center=new_center,
            units=self.units,
            dir=self.dir.as_tuple,
            clockwise=self.clockwise
        )
        self._replace_entity(new_entity)
        return new_entity
    
    @override
    def mirror(self, line_start: tuple[float, float], line_end: tuple[float, float]):

        mirror_start = Point2D.from_pair(line_start)
        mirror_end = Point2D.from_pair(line_end) 

        # to avoid confusion
        del line_start
        del line_end

        new_center = self._mirror_point(self.center, mirror_start, mirror_end)

        new_entity = SketchCircle(
            sketch=self._feature,
            radius=self.radius,
            center=new_center,
            units=self.units,
            dir=self.dir.as_tuple,
            clockwise=self.clockwise
        )

        self._replace_entity(new_entity)
        return new_entity

    @override
    def __repr__(self) -> str:
        return f"Circle(radius={self.radius}, center={self.center})"


class SketchLine(Entity):

    def __init__(
        self, sketch: "Sketch", start_point: Point2D, end_point: Point2D, units: UnitSystem
    ) -> None:

        self._sketch = sketch
        self.start = start_point
        self.end = end_point
        self.units = units
        self.entity_id = self.generate_entity_id()

        dx = self.end.x - self.start.x
        dy = self.end.y - self.start.y

        length = math.sqrt(dx**2 + dy**2)
        theta = math.atan2(dy, dx)
        unit_direction = Point2D(math.cos(theta), math.sin(theta))

        self.length = abs(length)
        self.dir = unit_direction

    @property
    @override
    def _feature(self):
        return self._sketch
    
    @override
    def rotate(self, origin: tuple[float, float], theta: float):

        new_start = self._rotate_point(self.start, Point2D.from_pair(origin), degrees=theta)
        new_end = self._rotate_point(self.end, Point2D.from_pair(origin), degrees=theta)

        new_entity =  SketchLine(
            sketch=self._sketch,
            start_point=new_start,
            end_point=new_end,
            units=self.units
        )
        self._replace_entity(new_entity)
        return new_entity
    
    @override
    def mirror(self, line_start: tuple[float, float], line_end: tuple[float, float]):

        mirror_start = Point2D.from_pair(line_start)
        mirror_end = Point2D.from_pair(line_end) 

        # to avoid confusion
        del line_start
        del line_end
        
        new_start = self._mirror_point(self.start, mirror_start, mirror_end)
        new_end = self._mirror_point(self.end, mirror_start, mirror_end)

        new_entity = SketchLine(
            sketch=self._sketch,
            start_point=new_start,
            end_point=new_end,
            units=self.units
        )
        self._replace_entity(new_entity)
        return new_entity
        
    
    @override
    def translate(self, x: float = 0, y: float = 0):
        
        new_start = Point2D(self.start.x + x, self.start.y + y)
        new_end = Point2D(self.end.x + x, self.end.y + y)

        new_entity = SketchLine(
            sketch=self._sketch,
            start_point=new_start,
            end_point=new_end,
            units=self.units
        )
        self._replace_entity(new_entity)
        return new_entity


    @override
    def to_model(self) -> model.SketchCurveSegmentEntity:
        return model.SketchCurveSegmentEntity(
            entityId=self.entity_id,
            startPointId=f"{self.entity_id}.start",
            endPointId=f"{self.entity_id}.end",
            startParam=0,
            endParam=self.length,
            geometry={
                "btType": "BTCurveGeometryLine-117",
                "pntX": self.start.x,
                "pntY": self.start.y,
                "dirX": self.dir.x,
                "dirY": self.dir.y,
            },
        )
    

    @override
    def __repr__(self) -> str:
        return f"Line(start={self.start}, end={self.end})"


class SketchArc(Entity):
    def __init__(
        self,
        sketch: "Sketch",
        radius: float,
        center: Point2D,
        theta_interval: tuple[float, float],
        units: UnitSystem,
        dir: tuple[float, float] = (1, 0),
        clockwise: bool = False,
    ):
        """
        Args:
            radius: The radius of the arc
            center: The centerpoint of the arc
            theta_interval: The theta interval, in degrees
            units: The unit system to use
            dir: An optional dir to specify. Defaults to +x axis
            clockwise: Whether or not the arc is clockwise. Defaults to false
        """

        self._sketch = sketch
        self.radius = radius
        self.center = center
        self.theta_interval = theta_interval
        self.dir = dir
        self.clockwise = clockwise
        self.entity_id = self.generate_entity_id()
        self.units = units


    @property
    @override
    def _feature(self):
        return self._sketch
    
    @override
    def mirror(self, line_start: tuple[float, float], line_end: tuple[float, float]) -> "SketchArc":
        

        mirror_start = Point2D.from_pair(line_start)
        mirror_end = Point2D.from_pair(line_end) 

        # to avoid confusion
        del line_start
        del line_end

        start_point = Point2D(
            self.radius * math.cos(self.theta_interval[0]) + self.center.x,
            self.radius * math.sin(self.theta_interval[0]) + self.center.y,
        )

        start_point = self._mirror_point(start_point, mirror_start, mirror_end)
        new_center = self._mirror_point(self.center, mirror_start, mirror_end)

        arc_start_vector = np.array([start_point.x - new_center.x, start_point.y - new_center.y])
        mirror_line_vector = np.array([mirror_end.x-mirror_start.x, mirror_end.y-mirror_start.y])

        angle_offset = 2 * math.acos( 
                                    np.dot(arc_start_vector, mirror_line_vector) / 
                                    (np.linalg.norm(arc_start_vector) * np.linalg.norm(mirror_line_vector))
                                    )
        
        d_theta = self.theta_interval[1] - self.theta_interval[0]
        
        new_theta = (
            (self.theta_interval[0] - angle_offset - d_theta),
            (self.theta_interval[0] - angle_offset), 
            )
        
        new_entity = SketchArc(
            sketch=self._sketch,
            radius=self.radius,
            center=new_center,
            theta_interval=new_theta,
            units=self.units,
            dir=self.dir, 
            clockwise=self.clockwise
        )
        self._replace_entity(new_entity)
        return new_entity

    
    @override
    def translate(self, x: float = 0, y: float = 0) -> "SketchArc":
        new_center = Point2D(self.center.x + x, self.center.y + y)
        new_entity = SketchArc(
            sketch=self._sketch,
            radius=self.radius,
            center=new_center,
            theta_interval=self.theta_interval,
            units=self.units,
            dir=self.dir,
            clockwise=self.clockwise
        )
        self._replace_entity(new_entity)
        return new_entity
    
    @override
    def rotate(self, origin: tuple[float, float], theta: float) -> "SketchArc":
        
        pivot = Point2D.from_pair(origin)

        start_point = Point2D(
            self.radius * math.cos(self.theta_interval[0]) + self.center.x,
            self.radius * math.sin(self.theta_interval[0]) + self.center.y,
        )

        new_center = self._rotate_point(self.center, pivot, theta)
        start_point = self._rotate_point(start_point, pivot, theta)

        d_theta = self.theta_interval[1] - self.theta_interval[0]
        
        arc_start_vector = np.array([start_point.x - new_center.x, start_point.y - new_center.y])
        x_axis = np.array([1,0])

        angle_start = math.acos(
            np.dot(arc_start_vector, x_axis) /
            np.linalg.norm(arc_start_vector)
        )

        new_theta = (
            angle_start,
            angle_start + d_theta
        )

        new_entity = SketchArc(
            sketch=self._sketch,
            radius=self.radius,
        center=new_center,
            theta_interval=new_theta,
            units=self.units,
            dir=self.dir,
            clockwise=self.clockwise
        )
        self._replace_entity(new_entity)
        return new_entity






    @override
    def to_model(self) -> model.SketchCurveSegmentEntity:
        return model.SketchCurveSegmentEntity(
            startPointId=f"{self.entity_id}.start",
            endPointId=f"{self.entity_id}.end",
            startParam=self.theta_interval[0],
            endParam=self.theta_interval[1],
            centerId=f"{self.entity_id}.center",
            entityId=f"{self.entity_id}",
            geometry={
                "btType": "BTCurveGeometryCircle-115",
                "radius": self.radius,
                "xcenter": self.center.x,
                "ycenter": self.center.y,
                "xdir": self.dir[0],
                "ydir": self.dir[1],
            },
        )

    @override
    def __repr__(self) -> str:
        return f"Arc(center={self.center}, radius={self.radius}, interval={self.theta_interval[0]}<θ<{self.theta_interval[1]})"
