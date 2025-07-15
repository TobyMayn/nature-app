from abc import ABC, abstractmethod

from exceptions import InvalidAlgorithmException
from ortho_analysis import OrthoAnalysis
from satellite_analysis import SatelliteAnalysis


class AbstractAlgorithmFactory(ABC):
    """Abstract class for creating analysis objects"""
    @abstractmethod
    def create_algorithm(type: str):
        pass



class ConcreteAlgorithmFactory(AbstractAlgorithmFactory):
    def create_algorithm(self, type: str):
        match type:
            case "orthophoto":
                return OrthoAnalysis()
            case "satelitte":
                return SatelliteAnalysis()
            case _:
                raise InvalidAlgorithmException()
