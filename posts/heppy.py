import turtle

bg = turtle.Screen()
bg.bgcolor("light blue")

img = turtle.Turtle()
img.shape("turtle")
img.speed(75)

# draw lines
img.penup()
img.goto(-190, -180)
img.color("yellow")
img.pensize(6)
img.pendown()
img.goto(190, -180)
img.penup()

img.penup()
img.goto(-160, -150)
img.color("purple")
img.pensize(6)
img.pendown()
img.goto(160, -150)
img.penup()

img.penup()
img.goto(-130, -120)
img.color("teal")
img.pensize(6)
img.pendown()
img.goto(130, -120)
img.penup()

# draw cake
img.goto(-74, -110)
img.pendown()
img.color("white")
img.goto(50, -110)
img.left(90)
img.forward(60)
img.left(90)
img.forward(125)
img.left(90)
img.forward(60)
img.penup()

# draw candles
img.goto(-60, -40)
img.color("aquamarine")
img.pendown()
img.pensize(3)
img.goto(-60, -20)
img.penup()

img.goto(-40, -40)
img.color("yellow")
img.pendown()
img.pensize(3)
img.goto(-40, -20)
img.penup()

img.goto(-20, -40)
img.color("green")
img.pendown()
img.pensize(3)
img.goto(-20, -20)
img.penup()

img.goto(0, -40)
img.color("pink")
img.pendown()
img.pensize(3)
img.goto(0, -20)
img.penup()

img.goto(20, -40)
img.color("blue")
img.pendown()
img.pensize(3)
img.goto(20, -20)
img.penup()

# print message
img.goto(-110, 35)
img.color("grey")
img.pendown()
img.write("C днём рождения!", font="24pt")

# send the turtle to the corner
img.penup()
img.goto(-250, 250)
while True:
    pass