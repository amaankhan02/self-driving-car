from enum import Enum;
# from Computer.NN_Trainer.Normalize import normalize_zero_to_one, normalize_negOne_to_one

class NormalizationMethod(Enum):
    zero_to_one = "zero_to_one"
    negOne_to_one = "negOne_to_one"
    none = "none"