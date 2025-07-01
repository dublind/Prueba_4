#conversor  de temperatura
import time
def celsius_to_fahrenheit(celsius):
    return (celsius * 9/5) + 32

def celsius_to_kelvin(celsius):
    return celsius + 273.15

print("Conversor de temperatura!")
time.sleep(1)
print("Ingrese una temperatura en grados Celsius:")
celsius = float(input())
fahrenheit = celsius_to_fahrenheit(celsius)
kelvin = celsius_to_kelvin(celsius)
print(f"{celsius} grados Celsius son {fahrenheit} grados Fahrenheit.")
print(f"{celsius} grados Celsius son {kelvin} Kelvin.")
print("¡Conversión completada!")

