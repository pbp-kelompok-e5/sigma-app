"""
Django Icon Design System - FIXED
==================================
A comprehensive icon component system for Django templates.

Usage in templates:
{% load icon_tags %}

Basic usage:
{% icon 'user' %}

With custom size and color:
{% icon 'trash' size='32' color='#FF0000' %}

With CSS classes:
{% icon 'plus' class='my-custom-class' %}
"""

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


class IconRegistry:
    """Central registry for all SVG icons"""
    
    ICONS = {
        'user': '''<path fill="currentColor" d="M12 2C9.243 2 7 4.243 7 7s2.243 5 5 5 5-2.243 5-5-2.243-5-5-5zm0 8c-1.654 0-3-1.346-3-3s1.346-3 3-3 3 1.346 3 3-1.346 3-3 3zm9 11v-1c0-3.859-3.141-7-7-7h-4c-3.86 0-7 3.141-7 7v1h2v-1c0-2.757 2.243-5 5-5h4c2.757 0 5 2.243 5 5v1h2z"/>''',
        
        'trash': '''<path fill="currentColor" d="M19 4h-3.5l-1-1h-5l-1 1H5v2h14M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12z"/>''',
        
        'plus': '''<path fill="currentColor" d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>''',
        
        'home': '''<path fill="currentColor" d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8h5z"/>''',
        
        'x': '''<path fill="currentColor" d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12 19 6.41z"/>''',
        
        'search': '''<path fill="currentColor" d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/>''',
        
        'filter': '''<path fill="currentColor" d="M10 18h4v-2h-4v2zM3 6v2h18V6H3zm3 7h12v-2H6v2z"/>''',
        
        'profile': '''<path fill="currentColor" d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>''',
        
        'edit': '''<path fill="currentColor" d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/>''',
        
        'settings': '''<path fill="currentColor" d="M19.14 12.94c.04-.3.06-.61.06-.94 0-.32-.02-.64-.07-.94l2.03-1.58c.18-.14.23-.41.12-.61l-1.92-3.32c-.12-.22-.37-.29-.59-.22l-2.39.96c-.5-.38-1.03-.7-1.62-.94l-.36-2.54c-.04-.24-.24-.41-.48-.41h-3.84c-.24 0-.43.17-.47.41l-.36 2.54c-.59.24-1.13.57-1.62.94l-2.39-.96c-.22-.08-.47 0-.59.22L2.74 8.87c-.12.21-.08.47.12.61l2.03 1.58c-.05.3-.07.62-.07.94s.02.64.07.94l-2.03 1.58c-.18.14-.23.41-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.24.24.41.48.41h3.84c.24 0 .44-.17.47-.41l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32c.12-.22.07-.47-.12-.61l-2.01-1.58zM12 15.6c-1.98 0-3.6-1.62-3.6-3.6s1.62-3.6 3.6-3.6 3.6 1.62 3.6 3.6-1.62 3.6-3.6 3.6z"/>''',
        
        'add': '''<path fill="currentColor" d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>''',
        
        'calendar': '''<path fill="currentColor" d="M19 4h-1V2h-2v2H8V2H6v2H5c-1.11 0-1.99.9-1.99 2L3 20c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 16H5V10h14v10zM9 14H7v-2h2v2zm4 0h-2v-2h2v2zm4 0h-2v-2h2v2zm-8 4H7v-2h2v2zm4 0h-2v-2h2v2zm4 0h-2v-2h2v2z"/>''',
            
        'clock': '''<path fill="currentColor" d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z"/>''',

        'trophy': '''<path fill="currentColor" d="M19 5h-2V3H7v2H5c-1.1 0-2 .9-2 2v1c0 2.55 1.92 4.63 4.39 4.94.63 1.5 1.98 2.63 3.61 2.96V19H7v2h10v-2h-4v-3.1c1.63-.33 2.98-1.46 3.61-2.96C19.08 12.63 21 10.55 21 8V7c0-1.1-.9-2-2-2zM5 8V7h2v3.82C5.84 10.4 5 9.3 5 8zm7 6c-1.65 0-3-1.35-3-3V5h6v6c0 1.65-1.35 3-3 3zm7-6c0 1.3-.84 2.4-2 2.82V7h2v1z"/>''',

        'star': '''<path fill="currentColor" d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"/>''',

        'award': '''<path fill="currentColor" d="M12 2L9 9l-7 .75 5.32 4.8L5.82 21 12 17.27 18.18 21l-1.5-6.45L22 9.75 15 9l-3-7z"/>''',

        'chart': '''<path fill="currentColor" d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zM9 17H7v-7h2v7zm4 0h-2V7h2v10zm4 0h-2v-4h2v4z"/>''',

        'history': '''<path fill="currentColor" d="M13 3c-4.97 0-9 4.03-9 9H1l3.89 3.89.07.14L9 12H6c0-3.87 3.13-7 7-7s7 3.13 7 7-3.13 7-7 7c-1.93 0-3.68-.79-4.94-2.06l-1.42 1.42C8.27 19.99 10.51 21 13 21c4.97 0 9-4.03 9-9s-4.03-9-9-9zm-1 5v5l4.28 2.54.72-1.21-3.5-2.08V8H12z"/>''',

        'check': '''<path fill="currentColor" d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>''',

        'inbox': '''<path fill="currentColor" d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5v-3h3.56c.69 1.19 1.97 2 3.44 2s2.75-.81 3.44-2H19v3zm0-5h-4.99c0 1.1-.9 2-2 2s-2-.9-2-2H5V5h14v9z"/>''',

        'info': '''<path fill="currentColor" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/>''',

        'eye': '''<path fill="currentColor" d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"/>''',

        'eye-off': '''<path fill="currentColor" d="M12 7c2.76 0 5 2.24 5 5 0 .65-.13 1.26-.36 1.83l2.92 2.92c1.51-1.26 2.7-2.89 3.43-4.75-1.73-4.39-6-7.5-11-7.5-1.4 0-2.74.25-3.98.7l2.16 2.16C10.74 7.13 11.35 7 12 7zM2 4.27l2.28 2.28.46.46C3.08 8.3 1.78 10.02 1 12c1.73 4.39 6 7.5 11 7.5 1.55 0 3.03-.3 4.38-.84l.42.42L19.73 22 21 20.73 3.27 3 2 4.27zM7.53 9.8l1.55 1.55c-.05.21-.08.43-.08.65 0 1.66 1.34 3 3 3 .22 0 .44-.03.65-.08l1.55 1.55c-.67.33-1.41.53-2.2.53-2.76 0-5-2.24-5-5 0-.79.2-1.53.53-2.2zm4.31-.78l3.15 3.15.02-.16c0-1.66-1.34-3-3-3l-.17.01z"/>''',
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
def icon(name, size='md', color='primary', css_class='', **kwargs):
    """
    Render an SVG icon
    
    Args:
        name: Icon name
        size: Size preset (xs, sm, md, lg, xl) or custom pixel value
        color: Color preset or hex/rgb value
        css_class: Additional CSS classes
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
        attr_name = key.replace('_', '-')
        attrs.append(f'{attr_name}="{value}"')
    
    attrs_str = ' ' + ' '.join(attrs) if attrs else ''
    class_str = f' class="{css_class}"' if css_class else ''
    
    # Get icon path and replace currentColor
    icon_path = IconRegistry.ICONS[name].replace('currentColor', color_value)
    
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{size_value}" height="{size_value}" viewBox="0 0 24 24" fill="none"{class_str}{attrs_str}>
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
    """Python class for generating icons programmatically in views"""
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