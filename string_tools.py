#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 22 18:34:43 2023
## Código implementado con ayuda de ChatGPT-4: openai
@author: nicalcoca
"""

## Para segmentar textos en líneas del mismo tamaño
def split_text_in_equal_lines(text, line_length):
    return '\n'.join(text[i:i+line_length] for i in range(0, len(text), line_length))