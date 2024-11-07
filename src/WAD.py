import sys
if sys.version_info[0] < 3.11:
    from typing_extensions import Self
elif sys.version_info[0] == 3 and sys.version_info[1] >= 11:
    from typing import Self
else:
    raise Exception("Unsupported Python version")

class WAD:

    precision = 18
    scalar = 10 ** precision

    def __init__(self, value, precision=18, preset_precision=False):
        match value:
            case str():
                if "." in value:
                    whole_part, decimal_part = value.split(".")
                    decimal_part = (decimal_part + "0" * precision)[:precision]
                    self.value = int(whole_part + decimal_part)
                else:
                    self.value = int(value) * 10**precision

            case float():
                self.value = int(value * 10**precision)

            case int():
                if not preset_precision:
                    self.value = value * 10**precision
                else:
                    self.value = value

            case WAD():
                if preset_precision or value.precision == precision:
                    self.value = value.value
                else:
                    precision_diff = value.precision - precision
                    self.value = int(value.value * 10**precision_diff)

            case _:
                raise TypeError("Unsupported type for value")

        # Set the precision and scalar values
        self.precision = precision
        self.scalar = 10**precision

    @classmethod
    def with_precision(cls, value, current_precision, new_precision):
        return WAD(value, current_precision, True).convert_precision(current_precision, new_precision)

    def convert_precision(self, current_precision, new_precision):
        precision_diff = new_precision - current_precision
        if precision_diff == 0:
            return self
        if precision_diff > 0:
            v = int(self.value * 10 ** precision_diff)
            return WAD(v, new_precision, True)
        if precision_diff < 0:    
            v = int(self.value // 10 ** abs(precision_diff))
            return WAD(v, new_precision, True)

    def as_float(self) -> float:
        return self.value / self.scalar

    def as_float_str(self):
        v = str(self.value)
        if len(v) <= self.precision:
            return f"0.{v.zfill(self.precision)}"
        return f"{v[:-self.precision]}.{v[-self.precision:]}"

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return str(self.value)

    def __class__(self) -> str:
        return "WAD"

    def __add__(self, other: Self) -> Self:
        if isinstance(other, int):
            return WAD(self.value + other, self.precision, True)
        elif isinstance(other, WAD):
            assert self.precision == other.precision, "Add failed: precision mismatch"
            return WAD(self.value + other.value, self.precision, True)

    def __sub__(self, other: Self) -> Self:
        assert self.precision == other.precision, "Subtract failed: precision mismatch"
        return WAD(self.value - other.value, self.precision, True)

    def __mul__(self, other) -> Self:
        if isinstance(other, int):
            return WAD(self.value * other, self.precision, True)
        elif isinstance(other, WAD):
            return WAD(self.value * other.value, self.precision + other.precision, True)
        elif isinstance(other, float):
            return WAD(int(self.value * other), self.precision, True)

    def __rmul__(self, other) -> Self:
        return self.__mul__(other)

    def mul(self, other: int, result_precision, other_precision: int = 0) -> Self:
        if isinstance(other, WAD):
            return WAD.with_precision(self.value * other.value, self.precision + other.precision, result_precision)
        elif isinstance(other, int):
            return WAD.with_precision(self.value * other, self.precision + other_precision, result_precision)
        elif isinstance(other, float):
            return WAD.with_precision(int(self.value * other), self.precision, result_precision)

    def __truediv__(self, other: Self) -> Self:
        v = int(self.value * 10 ** other.precision) // other.value
        return WAD(v, self.precision, True)

    def div(self, other: int, result_precision) -> Self:
        return WAD.with_precision(
            (self.value * 10 ** other.precision) // other, 
            self.precision,
            result_precision
        )
