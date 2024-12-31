import math

# Function to calculate the area of a circle
def calculate_circle_area(radius):
    if radius < 0:
        return "Radius cannot be negative."
    area = math.pi * radius**2
    return area

# Input radius from the user
try:
    radius = float(input("Enter the radius of the circle: "))
    area = calculate_circle_area(radius)
    print(f"The area of the circle with radius {radius} is: {area:.2f}")
except ValueError:
    print("Please enter a valid number for the radius.")