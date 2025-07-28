from abc import ABC, abstractmethod

# import ortho_analysis
# import satellite_analysis
# from exceptions import InvalidAlgorithmException


class AbstractAlgorithmFactory(ABC):
    """Abstract class for creating analysis objects"""
    @abstractmethod
    def create_algorithm(type: str):
        pass



class ConcreteAlgorithmFactory(AbstractAlgorithmFactory):
    def create_algorithm(self, type: str):
        # match type:
        #     case "orthophoto":
        #         return ortho_analysis.OrthoAnalysis()
        #     case "satelitte":
        #         return satellite_analysis.SatelliteAnalysis()
        #     case _:
        #         raise InvalidAlgorithmException()
        pass
