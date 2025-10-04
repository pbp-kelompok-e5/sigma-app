"""
Django Icon Design System
=========================
A comprehensive icon component system for Django templates.

Usage in templates:
{% load icon_tags %}

Basic usage:
{% icon 'user' %}

With custom size and color:
{% icon 'trash' size='32' color='#FF0000' %}

With CSS classes:
{% icon 'plus' class='my-custom-class' %}

Available icons: user, trash, plus, home, x, search, filter, profile, edit, 
                 settings, calendar, clock, add
"""

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


class IconRegistry:
    """Central registry for all SVG icons"""
    
    ICONS = {
        'user': '''<path fill="currentColor" d="M6.5 7.5C6.5 6.04131 7.07946 4.64236 8.11091 3.61091C9.14236 2.57946 10.5413 2 12 2C13.4587 2 14.8576 2.57946 15.8891 3.61091C16.9205 4.64236 17.5 6.04131 17.5 7.5C17.5 8.95869 16.9205 10.3576 15.8891 11.3891C14.8576 12.4205 13.4587 13 12 13C10.5413 13 9.14236 12.4205 8.11091 11.3891C7.07946 10.3576 6.5 8.95869 6.5 7.5ZM3 19C3 17.6739 3.52678 16.4021 4.46447 15.4645C5.40215 14.5268 6.67392 14 8 14H16C17.3261 14 18.5979 14.5268 19.5355 15.4645C20.4732 16.4021 21 17.6739 21 19V22H3V19Z"/>''',
        
        'trash': '''<path fill="currentColor" d="M19 4H15.5L14.5 3H9.5L8.5 4H5V6H19M6 19C6 19.5304 6.21071 20.0391 6.58579 20.4142C6.96086 20.7893 7.46957 21 8 21H16C16.5304 21 17.0391 20.7893 17.4142 20.4142C17.7893 20.0391 18 19.5304 18 19V7H6V19Z"/>''',
        
        'plus': '''<path fill="currentColor" d="M20 13.1429H13.1429V20H10.8571V13.1429H4V10.8571H10.8571V4H13.1429V10.8571H20V13.1429Z"/>''',
        
        'home': '''<path fill="currentColor" d="M4 21V9L12 3L20 9V21H14V14H10V21H4Z"/>''',
        
        'x': '''<path fill="currentColor" d="M5.6 21L4 19.4L10.4 13L4 6.6L5.6 5L12 11.4L18.4 5L20 6.6L13.6 13L20 19.4L18.4 21L12 14.6L5.6 21Z"/>''',
        
        'search': '''<path fill="currentColor" d="M19.6 21L13.3 14.7C12.8 15.1 12.225 15.4167 11.575 15.65C10.925 15.8833 10.2333 16 9.5 16C7.68333 16 6.146 15.3707 4.888 14.112C3.63 12.8533 3.00067 11.316 3 9.5C2.99933 7.684 3.62867 6.14667 4.888 4.888C6.14733 3.62933 7.68467 3 9.5 3C11.3153 3 12.853 3.62933 14.113 4.888C15.373 6.14667 16.002 7.684 16 9.5C16 10.2333 15.8833 10.925 15.65 11.575C15.4167 12.225 15.1 12.8 14.7 13.3L21 19.6L19.6 21ZM9.5 14C10.75 14 11.8127 13.5627 12.688 12.688C13.5633 11.8133 14.0007 10.7507 14 9.5C13.9993 8.24933 13.562 7.187 12.688 6.313C11.814 5.439 10.7513 5.00133 9.5 5C8.24867 4.99867 7.18633 5.43633 6.313 6.313C5.43967 7.18967 5.002 8.252 5 9.5C4.998 10.748 5.43567 11.8107 6.313 12.688C7.19033 13.5653 8.25267 14.0027 9.5 14Z"/>''',
        
        'filter': '''<path fill="currentColor" d="M19.6 21L13.3 14.7C12.8 15.1 12.225 15.4167 11.575 15.65C10.925 15.8833 10.2333 16 9.5 16C7.68333 16 6.146 15.3707 4.888 14.112C3.63 12.8533 3.00067 11.316 3 9.5C2.99933 7.684 3.62867 6.14667 4.888 4.888C6.14733 3.62933 7.68467 3 9.5 3C11.3153 3 12.853 3.62933 14.113 4.888C15.373 6.14667 16.002 7.684 16 9.5C16 10.2333 15.8833 10.925 15.65 11.575C15.4167 12.225 15.1 12.8 14.7 13.3L21 19.6L19.6 21ZM9.5 14C10.75 14 11.8127 13.5627 12.688 12.688C13.5633 11.8133 14.0007 10.7507 14 9.5C13.9993 8.24933 13.562 7.187 12.688 6.313C11.814 5.439 10.7513 5.00133 9.5 5C8.24867 4.99867 7.18633 5.43633 6.313 6.313C5.43967 7.18967 5.002 8.252 5 9.5C4.998 10.748 5.43567 11.8107 6.313 12.688C7.19033 13.5653 8.25267 14.0027 9.5 14Z"/>''',
        
        # Dashboard icons
        'profile': '''<path fill="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>''',
        
        'edit': '''<path fill="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>''',
        
        'settings': '''<path fill="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4"/>''',
        
        'add': '''<path fill="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"/>''',
        
        'calendar': '''<path fill="currentColor" fill-rule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clip-rule="evenodd"/>''',
            
        'clock': '''<path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>''',
    }
    
    SIZE_PRESETS = {
        'xs': 16,
        'sm': 20,
        'md': 24,  # default
        'lg': 32,
        'xl': 48,
    }
    
    COLOR_PRESETS = {
        'primary': '#00063D',
        'secondary': '#F26419',
        'success': '#10B981',
        'danger': '#EF4444',
        'warning': '#F59E0B',
        'info': '#3B82F6',
        'white': '#FFFFFF',
        'black': '#000000',
    }


@register.simple_tag
def icon(name, size='md', color='primary', css_class='', stroke=False, **kwargs):
    """
    Render an SVG icon
    
    Args:
        name: Icon name (user, trash, plus, home, x, search, filter, profile, 
              edit, settings, add, calendar, clock)
        size: Size preset (xs, sm, md, lg, xl) or custom pixel value
        color: Color preset or hex/rgb value
        css_class: Additional CSS classes
        stroke: If True, use stroke instead of fill (for outlined icons)
        **kwargs: Additional HTML attributes (aria_label, data_*, etc.)
    
    Returns:
        Safe HTML string containing the SVG icon
    """
    if name not in IconRegistry.ICONS:
        return mark_safe(f'<!-- Icon "{name}" not found -->')
    
    # Resolve size
    if size in IconRegistry.SIZE_PRESETS:
        size_value = IconRegistry.SIZE_PRESETS[size]
    else:
        try:
            size_value = int(size)
        except (ValueError, TypeError):
            size_value = 24
    
    # Resolve color
    if color in IconRegistry.COLOR_PRESETS:
        color_value = IconRegistry.COLOR_PRESETS[color]
    else:
        color_value = color
    
    # Build additional attributes
    attrs = []
    for key, value in kwargs.items():
        # Convert underscore to hyphen for HTML attributes
        attr_name = key.replace('_', '-')
        attrs.append(f'{attr_name}="{value}"')
    
    attrs_str = ' ' + ' '.join(attrs) if attrs else ''
    class_str = f' class="{css_class}"' if css_class else ''
    
    # Replace currentColor with actual color value
    icon_path = IconRegistry.ICONS[name].replace('currentColor', color_value)
    
    # Determine fill/stroke attributes
    fill_attr = 'none' if stroke else color_value
    stroke_attr = f' stroke="{color_value}"' if stroke else ''
    
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{size_value}" height="{size_value}" viewBox="0 0 24 24" fill="{fill_attr}"{stroke_attr}{class_str}{attrs_str}>
  {icon_path}
</svg>'''
    
    return mark_safe(svg)


@register.simple_tag
def icon_button(name, size='md', color='primary', css_class='', button_class='', **kwargs):
    """
    Render an icon wrapped in a button element
    
    Args:
        name: Icon name
        size: Size preset or custom value
        color: Color preset or custom value
        css_class: CSS classes for the icon
        button_class: CSS classes for the button
        **kwargs: Additional button attributes
    """
    icon_html = icon(name, size=size, color=color, css_class=css_class)
    
    attrs = []
    for key, value in kwargs.items():
        attr_name = key.replace('_', '-')
        attrs.append(f'{attr_name}="{value}"')
    
    attrs_str = ' ' + ' '.join(attrs) if attrs else ''
    btn_class = f' class="{button_class}"' if button_class else ''
    
    return mark_safe(f'<button type="button"{btn_class}{attrs_str}>{icon_html}</button>')


# Example component class for use in views
class Icon:
    """
    Python class for generating icons programmatically in views
    """
    def __init__(self, name, size='md', color='primary', css_class='', **attrs):
        self.name = name
        self.size = size
        self.color = color
        self.css_class = css_class
        self.attrs = attrs
    
    def render(self):
        """Render the icon as HTML string"""
        return icon(
            self.name,
            size=self.size,
            color=self.color,
            css_class=self.css_class,
            **self.attrs
        )
    
    def __str__(self):
        return self.render()
    
    def __html__(self):
        return self.render()


# Utility functions
def get_available_icons():
    """Return list of available icon names"""
    return list(IconRegistry.ICONS.keys())


def get_size_presets():
    """Return dictionary of size presets"""
    return IconRegistry.SIZE_PRESETS.copy()


def get_color_presets():
    """Return dictionary of color presets"""
    return IconRegistry.COLOR_PRESETS.copy()