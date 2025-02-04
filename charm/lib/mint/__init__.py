# TODO:
#
#   Element Types:
#       'box', vertical and horizontal
#       'list', vertical and horizontal
#       'grid'
#       'viewport'
#       'region'
#       'padding'
#       'frame'
#   Other Types:    
#       'state'
#       'animation'
#       'director'
#


class Scene:
    pass


class State:
    pass


class KeyFrame:
    pass


class ElementConstructor(type):
    
    def __new__(meta, name, parents, attrs):
        pass


class ElementState:
    pass


class Element(metaclass=ElementConstructor):
    pass



