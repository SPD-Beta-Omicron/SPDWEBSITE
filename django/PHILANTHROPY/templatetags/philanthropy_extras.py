from django import template

register = template.Library()

@register.filter(name='hours_remaining')
def hours_remaining(goal, current):
    return max(0, float(goal) - float(current))