# Third-Party Notices

## Character artwork

The whale-girl character images and press sounds in `src/deepseek_pet/assets/`
(`DSniang1.png`, `DSniang02.png`, `whale_bubble.png`, `bubble_main.png`,
`bubble_mid.png`, `bubble_small.png`, `Ya1.wav`, and the generated
`icon.ico`) come from:

- Project: **DeepSeek-Balance-Whale-Widget**
- Author: **MeteorNOX**
- Repository: https://github.com/MeteorNOX/DeepSeek-Balance-Whale-Widget
- License: MIT

`whale_bubble.png` is a derived asset: it contains only the hand-drawn thought
bubble from `DSniang02.png`, with the character layer removed (see
`scripts/make_bubble_layer.py`), so the bubble can be shown/hidden independently.
`bubble_main.png`, `bubble_mid.png`, and `bubble_small.png` are the three parts
of that bubble (large bubble, medium circle, small circle) used for the staged
reveal animation.

`Ya1.wav` is a lossless WAV conversion of the upstream `Ya1.mp3` duck press
sound, used for the once-per-click sound toggle.

This project is an independent Windows desktop application. It does **not**
require DSH (DeepSeek Harness), does not read the `.dsh` directory, and does not
use the DSH plugin runtime. The upstream project is credited only as the source
of the character artwork and as inspiration.

## Upstream MIT license

MIT License

Copyright (c) 2026 MeteorNOX

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
