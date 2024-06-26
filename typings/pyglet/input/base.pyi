"""
This type stub file was generated by pyright.
"""

import enum
from pyglet.event import EventDispatcher

"""Interface classes for `pyglet.input`.

.. versionadded:: 1.2
"""
_is_pyglet_doc_run = ...
class DeviceException(Exception):
    ...


class DeviceOpenException(DeviceException):
    ...


class DeviceExclusiveException(DeviceException):
    ...


class Sign(enum.Enum):
    POSITIVE = ...
    NEGATIVE = ...
    INVERTED = ...
    DEFAULT = ...


class Device:
    """Input device.

    :Ivariables:
        display : `pyglet.display.Display`
            Display this device is connected to.
        name : str
            Name of the device, as described by the device firmware.
        manufacturer : str
            Name of the device manufacturer, or ``None`` if the information is
            not available.
    """
    def __init__(self, display, name) -> None:
        ...
    
    @property
    def is_open(self): # -> bool:
        ...
    
    def open(self, window=..., exclusive=...): # -> None:
        """Open the device to begin receiving input from it.

        :Parameters:
            `window` : Window
                Optional window to associate with the device.  The behaviour
                of this parameter is device and operating system dependant.
                It can usually be omitted for most devices.
            `exclusive` : bool
                If ``True`` the device will be opened exclusively so that no
                other application can use it.  The method will raise
                `DeviceExclusiveException` if the device cannot be opened this
                way (for example, because another application has already
                opened it).
        """
        ...
    
    def close(self): # -> None:
        """Close the device. """
        ...
    
    def get_controls(self):
        """Get a list of controls provided by the device.

        :rtype: list of `Control`
        """
        ...
    
    def get_guid(self):
        """Get the device GUID, in SDL2 format.

        Return a str containing a unique device identification
        string. This is generated from the hardware identifiers,
        and is in the same format as was popularized by SDL2.
        GUIDs differ between platforms, but are generally 32
        hexidecimal characters.

        :rtype: str containing the device's GUID.
        """
        ...
    
    def __repr__(self): # -> str:
        ...
    


class Control(EventDispatcher):
    """Single value input provided by a device.

    A control's value can be queried when the device is open.  Event handlers
    can be attached to the control to be called when the value changes.

    The `min` and `max` properties are provided as advertised by the
    device; in some cases the control's value will be outside this range.

    :Ivariables:
        `name` : str
            Name of the control, or ``None`` if unknown
        `raw_name` : str
            Unmodified name of the control, as presented by the operating
            system; or ``None`` if unknown.
        `inverted` : bool
            If ``True``, the value reported is actually inverted from what the
            device reported; usually this is to provide consistency across
            operating systems.
    """
    def __init__(self, name, raw_name=..., inverted=...) -> None:
        ...
    
    @property
    def value(self): # -> None:
        """Current value of the control.

        The range of the value is device-dependent; for absolute controls
        the range is given by ``min`` and ``max`` (however the value may exceed
        this range); for relative controls the range is undefined.

        :type: float
        """
        ...
    
    @value.setter
    def value(self, newvalue): # -> None:
        ...
    
    def __repr__(self): # -> str:
        ...
    
    def on_change(self, value): # -> None:
        """The value changed.

        :Parameters:
            `value` : float
                Current value of the control.

        :event:
        """
        ...
    


class RelativeAxis(Control):
    """An axis whose value represents a relative change from the previous
    value.
    """
    X = ...
    Y = ...
    Z = ...
    RX = ...
    RY = ...
    RZ = ...
    WHEEL = ...
    @property
    def value(self):
        ...
    
    @value.setter
    def value(self, value): # -> None:
        ...
    


class AbsoluteAxis(Control):
    """An axis whose value represents a physical measurement from the device.

    The value is advertised to range over ``minimum`` and ``maximum``.

    :Ivariables:
        `minimum` : float
            Minimum advertised value.
        `maximum` : float
            Maximum advertised value.
    """
    X = ...
    Y = ...
    Z = ...
    RX = ...
    RY = ...
    RZ = ...
    HAT = ...
    HAT_X = ...
    HAT_Y = ...
    def __init__(self, name, minimum, maximum, raw_name=..., inverted=...) -> None:
        ...
    


class Button(Control):
    """A control whose value is boolean. """
    @property
    def value(self): # -> bool:
        ...
    
    @value.setter
    def value(self, newvalue): # -> None:
        ...
    
    if _is_pyglet_doc_run:
        def on_press(self): # -> None:
            """The button was pressed.

            :event:
            """
            ...
        
        def on_release(self): # -> None:
            """The button was released.

            :event:
            """
            ...
        


class Joystick(EventDispatcher):
    """High-level interface for joystick-like devices.  This includes a wide range
    of analog and digital joysticks, gamepads, controllers, and possibly even
    steering wheels and other input devices. There is unfortunately no easy way to
    distinguish between most of these different device types.

    For a simplified subset of Joysticks, see the :py:class:`~pyglet.input.Controller`
    interface. This covers a variety of popular game console controllers. Unlike
    Joysticks, Controllers have strictly defined layouts and inputs.

    To use a joystick, first call `open`, then in your game loop examine
    the values of `x`, `y`, and so on.  These values are normalized to the
    range [-1.0, 1.0]. 

    To receive events when the value of an axis changes, attach an 
    on_joyaxis_motion event handler to the joystick.  The :py:class:`~pyglet.input.Joystick` instance,
    axis name, and current value are passed as parameters to this event.

    To handle button events, you should attach on_joybutton_press and 
    on_joy_button_release event handlers to the joystick.  Both the :py:class:`~pyglet.input.Joystick`
    instance and the index of the changed button are passed as parameters to 
    these events.

    Alternately, you may attach event handlers to each individual button in 
    `button_controls` to receive on_press or on_release events.
    
    To use the hat switch, attach an on_joyhat_motion event handler to the
    joystick.  The handler will be called with both the hat_x and hat_y values
    whenever the value of the hat switch changes.

    The device name can be queried to get the name of the joystick.

    :Ivariables:
        `device` : `Device`
            The underlying device used by this joystick interface.
        `x` : float
            Current X (horizontal) value ranging from -1.0 (left) to 1.0
            (right).
        `y` : float
            Current y (vertical) value ranging from -1.0 (top) to 1.0
            (bottom).
        `z` : float
            Current Z value ranging from -1.0 to 1.0.  On joysticks the Z
            value is usually the throttle control.  On controllers the Z
            value is usually the secondary thumb vertical axis.
        `rx` : float
            Current rotational X value ranging from -1.0 to 1.0.
        `ry` : float
            Current rotational Y value ranging from -1.0 to 1.0.
        `rz` : float
            Current rotational Z value ranging from -1.0 to 1.0.  On joysticks
            the RZ value is usually the twist of the stick.  On game
            controllers the RZ value is usually the secondary thumb horizontal
            axis.
        `hat_x` : int
            Current hat (POV) horizontal position; one of -1 (left), 0
            (centered) or 1 (right).
        `hat_y` : int
            Current hat (POV) vertical position; one of -1 (bottom), 0
            (centered) or 1 (top).
        `buttons` : list of bool
            List of boolean values representing current states of the buttons.
            These are in order, so that button 1 has value at ``buttons[0]``,
            and so on.
        `x_control` : `AbsoluteAxis`
            Underlying control for `x` value, or ``None`` if not available.
        `y_control` : `AbsoluteAxis`
            Underlying control for `y` value, or ``None`` if not available.
        `z_control` : `AbsoluteAxis`
            Underlying control for `z` value, or ``None`` if not available.
        `rx_control` : `AbsoluteAxis`
            Underlying control for `rx` value, or ``None`` if not available.
        `ry_control` : `AbsoluteAxis`
            Underlying control for `ry` value, or ``None`` if not available.
        `rz_control` : `AbsoluteAxis`
            Underlying control for `rz` value, or ``None`` if not available.
        `hat_x_control` : `AbsoluteAxis`
            Underlying control for `hat_x` value, or ``None`` if not available.
        `hat_y_control` : `AbsoluteAxis`
            Underlying control for `hat_y` value, or ``None`` if not available.
        `button_controls` : list of `Button`
            Underlying controls for `buttons` values.
    """
    def __init__(self, device) -> None:
        ...
    
    def open(self, window=..., exclusive=...): # -> None:
        """Open the joystick device.  See `Device.open`. """
        ...
    
    def close(self): # -> None:
        """Close the joystick device.  See `Device.close`. """
        ...
    
    def on_joyaxis_motion(self, joystick, axis, value): # -> None:
        """The value of a joystick axis changed.

        :Parameters:
            `joystick` : `Joystick`
                The joystick device whose axis changed.
            `axis` : string
                The name of the axis that changed.
            `value` : float
                The current value of the axis, normalized to [-1, 1].
        """
        ...
    
    def on_joybutton_press(self, joystick, button): # -> None:
        """A button on the joystick was pressed.

        :Parameters:
            `joystick` : `Joystick`
                The joystick device whose button was pressed.
            `button` : int
                The index (in `button_controls`) of the button that was pressed.
        """
        ...
    
    def on_joybutton_release(self, joystick, button): # -> None:
        """A button on the joystick was released.

        :Parameters:
            `joystick` : `Joystick`
                The joystick device whose button was released.
            `button` : int
                The index (in `button_controls`) of the button that was released.
        """
        ...
    
    def on_joyhat_motion(self, joystick, hat_x, hat_y): # -> None:
        """The value of the joystick hat switch changed.

        :Parameters:
            `joystick` : `Joystick`
                The joystick device whose hat control changed.
            `hat_x` : int
                Current hat (POV) horizontal position; one of -1 (left), 0
                (centered) or 1 (right).
            `hat_y` : int
                Current hat (POV) vertical position; one of -1 (bottom), 0
                (centered) or 1 (top).
        """
        ...
    
    def __repr__(self): # -> str:
        ...
    


class Controller(EventDispatcher):
    def __init__(self, device, mapping) -> None:
        """High-level interface for Game Controllers.

        Unlike Joysticks, Controllers have a strictly defined set of inputs
        that matches the layout of popular home video game console Controllers.
        This includes a variety of face and shoulder buttons, analog sticks and
        triggers, a directional pad, and optional rumble (force feedback)
        effects.

        To use a Controller, you must first call `open`. Controllers will then
        dispatch a variety of events whenever the inputs change. They can also
        be polled at any time to find the current value of any inputs. Analog
        sticks are normalized to the range [-1.0, 1.0], and triggers are
        normalized to the range [0.0, 1.0].

        :note: A running application event loop is required

        The following event types are dispatched:
            `on_button_press`
            `on_button_release`
            `on_stick_motion`
            `on_dpad_motion`
            `on_trigger_motion`

        The device name can be queried to get the name of the joystick.

        :Ivariables:
            `device` : `Device`
                The underlying device used by this joystick interface.
            `name` : str
                The name of the Controller as reported by the OS.
            `guid` : str
                The unique device identification string, in SDL2 format.
            `a` : bool
            `b` : bool
            `x` : bool
            `x` : bool
            `back` : bool
            `start` : bool
            `guide` : bool
            `leftshoulder` : bool
            `rightshoulder` : bool
            `leftstick` : bool
            `rightstick` : bool
            `leftx` : float
            `lefty` : float
            `rightx` : float
            `righty` : float
            `lefttrigger` : float
            `righttrigger` : float
            `dpadx`: float
            `dpady`: float

        .. versionadded:: 2.0
        """
        ...
    
    def open(self, window=..., exclusive=...): # -> None:
        """Open the controller.  See `Device.open`. """
        ...
    
    def close(self): # -> None:
        """Close the controller.  See `Device.close`. """
        ...
    
    def rumble_play_weak(self, strength=..., duration=...): # -> None:
        """Play a rumble effect on the weak motor.

        :Parameters:
            `strength` : float
                The strength of the effect, from 0 to 1.
            `duration` : float
                The duration of the effect in seconds.
        """
        ...
    
    def rumble_play_strong(self, strength=..., duration=...): # -> None:
        """Play a rumble effect on the strong motor.

        :Parameters:
            `strength` : float
                The strength of the effect, from 0 to 1.
            `duration` : float
                The duration of the effect in seconds.
        """
        ...
    
    def rumble_stop_weak(self): # -> None:
        """Stop playing rumble effects on the weak motor."""
        ...
    
    def rumble_stop_strong(self): # -> None:
        """Stop playing rumble effects on the strong motor."""
        ...
    
    def on_stick_motion(self, controller, stick, vector): # -> None:
        """The value of a controller analogue stick changed.

        :Parameters:
            `controller` : `Controller`
                The controller whose analogue stick changed.
            `stick` : string
                The name of the stick that changed.
            `vector` : Vec2
                A 2D vector representing the stick position.
                Each individual axis will be normalized from [-1, 1],
        """
        ...
    
    def on_dpad_motion(self, controller, vector): # -> None:
        """The direction pad of the controller changed.

        :Parameters:
            `controller` : `Controller`
                The controller whose hat control changed.
            `vector` : Vec2
                A 2D vector, representing the dpad position.
                Each individual axis will be one of [-1, 0, 1].
        """
        ...
    
    def on_trigger_motion(self, controller, trigger, value): # -> None:
        """The value of a controller analogue stick changed.

        :Parameters:
            `controller` : `Controller`
                The controller whose analogue stick changed.
            `trigger` : string
                The name of the trigger that changed.
            `value` : float
                The current value of the trigger, normalized to [0, 1].
        """
        ...
    
    def on_button_press(self, controller, button): # -> None:
        """A button on the controller was pressed.

        :Parameters:
            `controller` :  :py:class:`Controller`
                The controller whose button was pressed.
            `button` : string
                The name of the button that was pressed.
        """
        ...
    
    def on_button_release(self, controller, button): # -> None:
        """A button on the joystick was released.

        :Parameters:
            `controller` : `Controller`
                The controller whose button was released.
            `button` : string
                The name of the button that was released.
        """
        ...
    
    def __repr__(self): # -> str:
        ...
    


class AppleRemote(EventDispatcher):
    """High-level interface for Apple remote control.

    This interface provides access to the 6 button controls on the remote.
    Pressing and holding certain buttons on the remote is interpreted as
    a separate control.

    :Ivariables:
        `device` : `Device`
            The underlying device used by this interface.
        `left_control` : `Button`
            Button control for the left (prev) button.
        `left_hold_control` : `Button`
            Button control for holding the left button (rewind).
        `right_control` : `Button`
            Button control for the right (next) button.
        `right_hold_control` : `Button`
            Button control for holding the right button (fast forward).
        `up_control` : `Button`
            Button control for the up (volume increase) button.
        `down_control` : `Button`
            Button control for the down (volume decrease) button.
        `select_control` : `Button`
            Button control for the select (play/pause) button.
        `select_hold_control` : `Button`
            Button control for holding the select button.
        `menu_control` : `Button`
            Button control for the menu button.
        `menu_hold_control` : `Button`
            Button control for holding the menu button.
    """
    def __init__(self, device) -> None:
        ...
    
    def open(self, window=..., exclusive=...): # -> None:
        """Open the device.  See `Device.open`. """
        ...
    
    def close(self): # -> None:
        """Close the device.  See `Device.close`. """
        ...
    
    def on_button_press(self, button): # -> None:
        """A button on the remote was pressed.

        Only the 'up' and 'down' buttons will generate an event when the
        button is first pressed.  All other buttons on the remote will wait
        until the button is released and then send both the press and release
        events at the same time.

        :Parameters:
            `button` : unicode
                The name of the button that was pressed. The valid names are
                'up', 'down', 'left', 'right', 'left_hold', 'right_hold',
                'menu', 'menu_hold', 'select', and 'select_hold'
                
        :event:
        """
        ...
    
    def on_button_release(self, button): # -> None:
        """A button on the remote was released.

        The 'select_hold' and 'menu_hold' button release events are sent
        immediately after the corresponding press events regardless of
        whether the user has released the button.

        :Parameters:
            `button` : str
                The name of the button that was released. The valid names are
                'up', 'down', 'left', 'right', 'left_hold', 'right_hold',
                'menu', 'menu_hold', 'select', and 'select_hold'

        :event:
        """
        ...
    


class Tablet:
    """High-level interface to tablet devices.

    Unlike other devices, tablets must be opened for a specific window,
    and cannot be opened exclusively.  The `open` method returns a
    `TabletCanvas` object, which supports the events provided by the tablet.

    Currently only one tablet device can be used, though it can be opened on
    multiple windows.  If more than one tablet is connected, the behaviour is
    undefined.
    """
    def open(self, window):
        """Open a tablet device for a window.

        :Parameters:
            `window` : `Window`
                The window on which the tablet will be used.

        :rtype: `TabletCanvas`
        """
        ...
    


class TabletCanvas(EventDispatcher):
    """Event dispatcher for tablets.

    Use `Tablet.open` to obtain this object for a particular tablet device and
    window.  Events may be generated even if the tablet stylus is outside of
    the window; this is operating-system dependent.

    The events each provide the `TabletCursor` that was used to generate the
    event; for example, to distinguish between a stylus and an eraser.  Only
    one cursor can be used at a time, otherwise the results are undefined.

    :Ivariables:
        `window` : Window
            The window on which this tablet was opened.
    """
    def __init__(self, window) -> None:
        ...
    
    def close(self):
        """Close the tablet device for this window.
        """
        ...
    
    if _is_pyglet_doc_run:
        def on_enter(self, cursor): # -> None:
            """A cursor entered the proximity of the window.  The cursor may
            be hovering above the tablet surface, but outside of the window
            bounds, or it may have entered the window bounds.

            Note that you cannot rely on `on_enter` and `on_leave` events to
            be generated in pairs; some events may be lost if the cursor was
            out of the window bounds at the time.

            :Parameters:
                `cursor` : `TabletCursor`
                    The cursor that entered proximity.

            :event:
            """
            ...
        
        def on_leave(self, cursor): # -> None:
            """A cursor left the proximity of the window.  The cursor may have
            moved too high above the tablet surface to be detected, or it may
            have left the bounds of the window.

            Note that you cannot rely on `on_enter` and `on_leave` events to
            be generated in pairs; some events may be lost if the cursor was
            out of the window bounds at the time.

            :Parameters:
                `cursor` : `TabletCursor`
                    The cursor that left proximity.

            :event:
            """
            ...
        
        def on_motion(self, cursor, x, y, pressure, tilt_x, tilt_y, buttons): # -> None:
            """The cursor moved on the tablet surface.

            If `pressure` is 0, then the cursor is actually hovering above the
            tablet surface, not in contact.

            :Parameters:
                `cursor` : `TabletCursor`
                    The cursor that moved.
                `x` : int
                    The X position of the cursor, in window coordinates.
                `y` : int
                    The Y position of the cursor, in window coordinates.
                `pressure` : float
                    The pressure applied to the cursor, in range 0.0 (no
                    pressure) to 1.0 (full pressure).
                `tilt_x` : float
                    Currently undefined.
                `tilt_y` : float
                    Currently undefined.
                `buttons` : int
                    Button state may be provided if the platform supports it.
                    Supported on: Windows

            :event:
            """
            ...
        


class TabletCursor:
    """A distinct cursor used on a tablet.

    Most tablets support at least a *stylus* and an *erasor* cursor; this
    object is used to distinguish them when tablet events are generated.

    :Ivariables:
        `name` : str
            Name of the cursor.
    """
    def __init__(self, name) -> None:
        ...
    
    def __repr__(self): # -> str:
        ...
    


class ControllerManager(EventDispatcher):
    """High level interface for managing game Controllers.

    This class provides a convenient way to handle the
    connection and disconnection of devices. A list of all
    connected Controllers can be queried at any time with the
    `get_controllers` method. For hot-plugging, events are
    dispatched for `on_connect` and `on_disconnect`.
    To use the ControllerManager, first make an instance::

        controller_man = pyglet.input.ControllerManager()

    At the start of your game, query for any Controllers
    that are already connected::

        controllers = controller_man.get_controllers()

    To handle Controllers that are connected or disconnected
    after the start of your game, register handlers for the
    appropriate events::

        @controller_man.event
        def on_connect(controller):
            # code to handle newly connected
            # (or re-connected) controllers
            controller.open()
            print("Connect:", controller)

        @controller_man.event
        def on_disconnect(controller):
            # code to handle disconnected Controller
            print("Disconnect:", controller)

    .. versionadded:: 2.0
    """
    def get_controllers(self):
        """Get a list of all connected Controllers

        :rtype: list of :py:class:`Controller`
        """
        ...
    
    def on_connect(self, controller): # -> None:
        """A Controller has been connected. If this is
        a previously dissconnected Controller that is
        being re-connected, the same Controller instance
        will be returned.

        :Parameters:
            `controller` : :py:class:`Controller`
                An un-opened Controller instance.

        :event:
        """
        ...
    
    def on_disconnect(self, controller): # -> None:
        """A Controller has been disconnected.

        :Parameters:
            `controller` : :py:class:`Controller`
                An un-opened Controller instance.

        :event:
        """
        ...
    


