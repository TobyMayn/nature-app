from abc import ABC, abstractmethod

from algorithms.ortho_analysis import OrthoAnalysis
from algorithms.satellite_analysis import SatelitteAnalysis
from exceptions import InvalidAlgorithmException


class AbstractAlgorithmFactory(ABC):
    """Abstract class for creating analysis objects"""
    @abstractmethod
    def create_algorithm(type: str):
        pass



class ConcreteAlgorithmFactory(AbstractAlgorithmFactory):
    """ Concrete class implementation with analysis instantiation"""
    def create_algorithm(self, type: str):
        match type:
            case "orthophoto":
                return OrthoAnalysis(device="cpu")
            case "satelitte":
                return SatelitteAnalysis()
            case _:
                raise InvalidAlgorithmException()

