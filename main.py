#!/usr/bin/env python3

from argparse import ArgumentParser
from itertools import cycle
from pathlib import Path
from typing import Tuple

from gimpformats import GimpLayer
from gimpformats.gimpXcfDocument import GimpDocument

RGBA = Tuple[int, int, int, int]

LAYER_NAMES = ('Repaint', 'Repaint BLU', 'Repaint RED')


def split_str(s: str) -> Tuple[str]:
	return tuple(_s for _s in s.split(':') if _s)


def hex2rgba(hex: str) -> RGBA:
	hex = hex.lstrip('#')

	match len(hex):
		case 3:
			return (int(hex[0], 16), int(hex[1], 16), int(hex[2], 16), 255)
		case 6:
			return (int(hex[0:2], 16), int(hex[2:4], 16), int(hex[4:6], 16), 255)
		case 8:
			return (int(hex[0:2], 16), int(hex[2:4], 16), int(hex[4:6], 16), int(hex[6:8], 16))
		case _:
			raise ValueError(hex)


def hexs2rgba(hexs: str) -> Tuple[RGBA]:
	return tuple(map(hex2rgba, split_str(hexs)))


def recolor_layer(layer: GimpLayer, color: RGBA):
	frag = layer.image.load()

	for y in range(layer.image.height):
		for x in range(layer.image.width):
			frag[x, y] = color


if __name__ == '__main__':
	parser = ArgumentParser()
	parser.add_argument(
		'input_file',
		help='An XCF file to take as input.',
		type=Path
	)
	parser.add_argument(
		'colors',
		help='A colon-separated list of colors in hex format with optional preceding "#"s, and with optional alpha channels.',
		type=hexs2rgba,
	)
	parser.add_argument(
		'output_file',
		help='An image file to output to, defaults to a PNG with the same name as the input file.',
		type=Path, nargs='?'
	)

	args = parser.parse_args()

	if not len(args.colors):
		raise ValueError('colors must contain at least one valid color')

	args.output_file = args.output_file or args.input_file.parent / f'{args.input_file.stem}.png'

	project = GimpDocument(args.input_file)

	colors = cycle(args.colors)
	for layer in project._layers:
		if layer.name in LAYER_NAMES:
			recolor_layer(layer, next(args.colors))

	image = project.render(project.walkTree())
	image.save(args.output_file)
