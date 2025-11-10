# Adding Your Midjourney Background Image

## Steps:

1. **Generate image in Midjourney** using the prompt:
   ```
   A moody cinematic photograph of a lone vintage Russian television on a wooden stand in a misty birch forest at dusk, Cyrillic letters faintly glowing on the screen, fog rolling through white birch trees, dark teal and deep blue color grading, atmospheric haze, film grain, hyperrealistic photography, 8k, cinematic lighting, shallow depth of field, mystical Russian landscape --ar 16:9 --style raw --v 6
   ```

2. **Download the image** and save it as `background.jpg`

3. **Add to project**:
   - Place the image in `frontend/public/background.jpg`

4. **Update CSS**:
   - Open `frontend/app/globals.css`
   - Find line 37-39 and uncomment/update:
   ```css
   .bg-showcase {
     background-image: url('/background.jpg');
   }
   ```

5. **Restart dev server** to see changes

## Image specs:
- Aspect ratio: 16:9 (recommended)
- Size: 1920x1080 or higher
- Format: JPG or PNG
- Optimize for web (keep under 500KB for fast loading)

## Tips:
- Use darker, moodier images for better contrast with white sidebar
- Teal, blue, or gray tones work best
- High contrast images make the form stand out more
