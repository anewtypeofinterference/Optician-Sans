#!/usr/bin/env python3
"""Add the glyphs Optician Sans is missing for technical headlines.

    $  dollar        U+0024
    <  less          U+003C
    >  greater       U+003E
    ~  asciitilde    U+007E
    …  ellipsis      U+2026
    `  grave.quote   U+0060  (replaces the accent-height grave as the backtick)

The original `grave` glyph stays in the font untouched, because the accented
letters (À, È, …) are built from it; U+0060 is simply pointed at the new one.

The FontLab source (VFC/) can't be edited without FontLab, so this patches the
compiled fonts directly and regenerates the web fonts from them:

    OpenType-TT/Optician-Sans.ttf  ->  Web-TT/Optician-Sans.woff
    OpenType-PS/Optician-Sans.otf  ->  Web-PS/Optician-Sans.woff2

Every shape is built from measurements of the existing design: 100-unit
vertical stems, 90-unit horizontals, maths signs centred on y=250 in a 550
advance (matching plus, equal and multiply), and V's flat-cut terminals.

Safe to re-run: existing copies of these glyphs are redrawn, not duplicated.

Requires: pip install fonttools brotli skia-pathops
"""
from __future__ import annotations

import math
from pathlib import Path

from fontTools.pens.areaPen import AreaPen
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.reverseContourPen import ReverseContourPen
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont
import pathops

ROOT = Path(__file__).resolve().parent.parent
VERSION = 1.003

# Shared metrics, measured from the existing glyphs.
MATH_ADVANCE = 550  # plus, equal
MATH_LEFT, MATH_RIGHT = 75, 475
MATH_MID = 250  # vertical centre of plus/hyphen/equal
STEM = 100  # vertical stroke (I, bar)
BAR = 90  # horizontal stroke (hyphen, plus)


# ---------------------------------------------------------------- shapes
# Each function draws into a pen and returns the advance width. Contour
# direction doesn't matter here; it is normalised per font flavour later.


def draw_less(pen, glyphs) -> int:
	"""A V turned on its side: flat-cut terminals, flat outer apex."""
	polygon(pen, CHEVRON)
	return MATH_ADVANCE


def draw_greater(pen, glyphs) -> int:
	polygon(pen, [(MATH_ADVANCE - x, y) for x, y in CHEVRON])
	return MATH_ADVANCE


# Outer edges run from the 100-unit flat apex at the left to the full
# 50..450 height of the plus sign at the right; the arms are ~95 thick.
CHEVRON = [
	(475, 450),
	(75, 300),
	(75, 200),
	(475, 50),
	(475, 152),
	(214, 250),
	(475, 348),
]


def draw_asciitilde(pen, glyphs) -> int:
	"""A monoline wave, BAR thick, centred on the maths axis."""
	amplitude = 38
	u0, u1 = -0.17, 1.17  # a little more than one full period
	x0, x1 = MATH_LEFT + 22, MATH_RIGHT - 22

	def centre(u):
		x = x0 + (x1 - x0) * (u - u0) / (u1 - u0)
		return x, MATH_MID + amplitude * math.sin(2 * math.pi * u)

	def edge(u, side):
		e = 1e-4
		(xa, ya), (xb, yb) = centre(u - e), centre(u + e)
		dx, dy = xb - xa, yb - ya
		length = math.hypot(dx, dy)
		x, y = centre(u)
		return x - side * dy / length * BAR / 2, y + side * dx / length * BAR / 2

	def edge_curve(side, start, end, segments=8):
		"""Cubic segments along one offset edge (Hermite fit)."""
		out = []
		step = (end - start) / segments
		for i in range(segments):
			a, b = start + step * i, start + step * (i + 1)
			e = 1e-4
			pa, pb = edge(a, side), edge(b, side)
			da = [(q - p) / (2 * e) for p, q in zip(edge(a - e, side), edge(a + e, side))]
			db = [(q - p) / (2 * e) for p, q in zip(edge(b - e, side), edge(b + e, side))]
			h = (b - a) / 3
			out.append(
				(
					(pa[0] + da[0] * h, pa[1] + da[1] * h),
					(pb[0] - db[0] * h, pb[1] - db[1] * h),
					pb,
				)
			)
		return out

	def rounded(points):
		return [(round(x), round(y)) for x, y in points]

	pen.moveTo(rounded([edge(u0, 1)])[0])
	for segment in edge_curve(1, u0, u1):
		pen.curveTo(*rounded(segment))
	pen.lineTo(rounded([edge(u1, -1)])[0])
	for segment in edge_curve(-1, u1, u0):
		pen.curveTo(*rounded(segment))
	pen.closePath()
	return MATH_ADVANCE


def draw_ellipsis(pen, glyphs) -> int:
	"""Three periods on the period's own rhythm."""
	advance = glyphs['period'].width
	for i in range(3):
		glyphs['period'].draw(TransformPen(pen, (1, 0, 0, 1, advance * i, 0)))
	return advance * 3


def draw_dollar(pen, glyphs) -> int:
	"""A dollar with a slightly shortened S and stem stubs that reach a
	little past the baseline and cap height, so it reads as a dollar
	without towering over the capitals.

	Squashing the S would thin its horizontal strokes, so it is squashed a
	little further than needed and then thickened vertically back to the
	full BAR weight (three copies stacked a few units apart and merged).
	"""
	s = glyphs['S']
	outline = RecordingPen()
	s.draw(outline)
	xs = [p[0] for _, pts in outline.value for p in pts]
	ys = [p[1] for _, pts in outline.value for p in pts]
	s_bottom, s_height = min(ys), max(ys) - min(ys)
	mid = (min(xs) + max(xs)) / 2
	left, right = round(mid - STEM / 2), round(mid + STEM / 2)

	cap = glyphs['I']
	cap_outline = RecordingPen()
	cap.draw(cap_outline)
	cap_ys = [p[1] for _, pts in cap_outline.value for p in pts]
	overshoot = 40  # how far the stubs reach past the capitals
	inset = 25  # how far the S is pulled in from the baseline and cap height
	floor, ceiling = min(cap_ys) - overshoot, max(cap_ys) + overshoot
	stub = overshoot + inset  # visible length of each stub
	bite = 45  # how far each is buried in the S
	body_bottom, body_top = floor + stub, ceiling - stub
	body = body_top - body_bottom
	# Solve for the squash and the thickening together, so the body lands
	# exactly on its height and the horizontals come back to BAR.
	squash = (body - BAR) / (s_height - BAR)
	thicken = BAR * (1 - squash)

	path = pathops.Path()
	path_pen = path.getPen()
	for lift in (0, thicken / 2, thicken):
		s.draw(
			TransformPen(
				path_pen,
				(1, 0, 0, squash, 0, body_bottom + lift - s_bottom * squash),
			)
		)
	for y0, y1 in ((body_top - bite, ceiling), (floor, body_bottom + bite)):
		# Same winding as the S, so the union below treats them as ink.
		rect = RecordingPen()
		polygon(rect, [(left, y0), (right, y0), (right, y1), (left, y1)])
		if (area(rect) > 0) != (area(outline) > 0):
			reversed_rect = RecordingPen()
			rect.replay(ReverseContourPen(reversed_rect))
			rect = reversed_rect
		rect.replay(path_pen)
	path.simplify(fix_winding=True, keep_starting_points=True)
	assert len(list(path.contours)) == 1, 'dollar stubs did not merge into the S'
	path.draw(pen)
	return s.width


def draw_backtick(pen, glyphs) -> int:
	"""A backtick at quote height: the straight quote's 300..500 band and
	its 100-to-60 taper, leaning the way a grave does."""
	polygon(pen, [(65, 500), (170, 500), (245, 300), (185, 300)])
	return 310


def polygon(pen, points) -> None:
	pen.moveTo(points[0])
	for point in points[1:]:
		pen.lineTo(point)
	pen.closePath()


def area(recording: RecordingPen) -> float:
	pen = AreaPen()
	recording.replay(pen)
	return pen.value


GLYPHS = [
	# name, codepoint, drawing function
	('dollar', 0x0024, draw_dollar),
	('less', 0x003C, draw_less),
	('greater', 0x003E, draw_greater),
	('asciitilde', 0x007E, draw_asciitilde),
	('ellipsis', 0x2026, draw_ellipsis),
	('grave.quote', 0x0060, draw_backtick),
]


# ---------------------------------------------------------------- patching


def oriented(recording: RecordingPen, counter_clockwise: bool) -> RecordingPen:
	"""TrueType wants clockwise outer contours, PostScript the opposite."""
	if (area(recording) > 0) == counter_clockwise:
		return recording
	flipped = RecordingPen()
	recording.replay(ReverseContourPen(flipped))
	return flipped


def patch(font: TTFont) -> None:
	glyphs = font.getGlyphSet()
	is_truetype = 'glyf' in font
	order = font.getGlyphOrder()

	for name, codepoint, draw in GLYPHS:
		recording = RecordingPen()
		advance = draw(recording, glyphs)
		recording = oriented(recording, counter_clockwise=not is_truetype)
		is_new = name not in order
		if is_new:
			order.append(name)

		if is_truetype:
			pen = TTGlyphPen(None)
			recording.replay(Cu2QuPen(pen, max_err=0.5, reverse_direction=False))
			font['glyf'][name] = glyph = pen.glyph()
			glyph.recalcBounds(font['glyf'])
			left = glyph.xMin
		else:
			cff = font['CFF '].cff
			top = cff.topDictIndex[0]
			pen = T2CharStringPen(advance, None)
			recording.replay(pen)
			charstring = pen.getCharString(private=top.Private, globalSubrs=cff.GlobalSubrs)
			strings = top.CharStrings
			if is_new:
				strings.charStringsIndex.append(charstring)
				strings.charStrings[name] = len(strings.charStringsIndex) - 1
				# The charset can be the same list as the glyph order above.
				if name not in top.charset:
					top.charset.append(name)
			else:
				strings.charStringsIndex[strings.charStrings[name]] = charstring
			left = round(min(p[0] for _, pts in recording.value for p in pts))

		font['hmtx'][name] = (advance, left)
		for table in font['cmap'].tables:
			if table.isUnicode():
				table.cmap[codepoint] = name

	font.setGlyphOrder(order)
	if is_truetype:
		font['glyf'].glyphOrder = order
		# New glyphs carry no TrueType instructions.
		font['maxp'].numGlyphs = len(order)

	# The original signature can't survive a modification.
	if 'DSIG' in font:
		del font['DSIG']

	font['head'].fontRevision = VERSION
	for record in font['name'].names:
		if record.nameID == 5:
			record.string = f'Version {VERSION:.3f}'


def build(source: str, web: str, flavor: str) -> None:
	font = TTFont(ROOT / source)
	patch(font)
	font.save(ROOT / source)

	# Reload so the web font is made from exactly what was written.
	font = TTFont(ROOT / source)
	font.flavor = flavor
	font.save(ROOT / web)
	print(f'{source} -> {web}  ({len(font.getGlyphOrder())} glyphs)')


if __name__ == '__main__':
	build('OpenType-TT/Optician-Sans.ttf', 'Web-TT/Optician-Sans.woff', 'woff')
	build('OpenType-PS/Optician-Sans.otf', 'Web-PS/Optician-Sans.woff2', 'woff2')
