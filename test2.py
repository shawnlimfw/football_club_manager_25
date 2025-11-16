import math

def value_calibrated(ovr, age):
    A = 3.07
    B = 0.1784
    k = 0.0675
    OVR_REF = 70.0
    AGE_REF = 30.0

    value = A * math.exp(B * (ovr - OVR_REF) + k * (AGE_REF - age))
    return value * 1000000

examples = [(70, a) for a in range(16, 35, 2)]

for ovr, age in examples:
    print(f"OVR {ovr}, Age {age}: €{fifa_value_calibrated(ovr, age):,.0f}")
