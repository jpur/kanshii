import math

def complex_uvec(v):
	mag = math.sqrt(v.real**2 + v.imag**2)
	return complex(v.real/mag, v.imag/mag) if mag else complex(0, 0)

def complex_dot(a, b):
	return a.real * b.real + a.imag * b.imag