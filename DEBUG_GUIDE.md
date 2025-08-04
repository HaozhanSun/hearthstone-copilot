# Debugging Guide for Hearthstone Bot

This guide explains how to use the new screenshot logging features to debug image recognition issues.

## Overview

The bot now automatically saves screenshots during image recognition attempts to help you understand why detection might be failing. All screenshots are saved in the `screenshots/image_recognition_attempts/` directory.

## Screenshot Naming Convention

Screenshots are named with the following format:
```
YYYYMMDD_HHMMSS_mmm_ATTEMPT_TYPE_STATUS.png
```

For example:
- `20241201_143052_123_battlenet_full_screen_FAILED.png`
- `20241201_143052_456_battlenet_button_search_SUCCESS.png`

## Types of Screenshots

### 1. Battle.net Launch Screenshots

When you click "START (F10)", the bot saves several screenshots:

- **`battlenet_window_*`**: Battle.net window capture (not full screen)
- **`battlenet_ocr_search_*`**: Annotated image showing:
  - Green rectangle: Search area (bottom-left 40% of window, bottom 30% area)
  - Yellow rectangles: All detected "PLAY" text elements with confidence scores
  - OCR text detection results
- **`battlenet_ocr_matched_*`**: Success screenshot with red rectangle highlighting the matched "PLAY" text
- **`click_start_search_*`**: Search for "点击开始" (Click to Start) button
- **`click_start_matched_*`**: Success screenshot when "点击开始" button is clicked
- **`my_collection_search_*`**: Search for "我的收藏" (My Collection) button
- **`my_collection_matched_*`**: Success screenshot when "我的收藏" button is clicked
- **`hearthstone_collection_reached_*`**: Final screenshot confirming we're in the collection

### 2. Hearthstone Window Detection Screenshots

When you click "Detect Hearthstone Window":

- **`hearthstone_window_detection_*`**: Screenshot before/after window detection attempt

### 3. Component Test Screenshots

When you click "Test Components":

- **`component_test_screenshot_*`**: Screenshot captured during component testing

## How to Debug PLAY Button Detection

### Step 1: Run the Bot and Try to Launch

1. Run `python launcher.py` (now launches GUI directly)
2. Click "START (F10)" or press F10 to start the bot
3. Check the logs for detailed information
4. Look at the saved screenshots in `screenshots/image_recognition_attempts/`
5. Press F12 to stop the bot if needed

### Step 2: Analyze the Screenshots

Look for these files in the screenshots directory:

1. **`battlenet_window_FAILED.png`**: What the bot sees in the Battle.net window
2. **`battlenet_ocr_search_FAILED.png`**: Annotated image showing OCR search results
3. **`battlenet_ocr_matched_SUCCESS.png`**: Success screenshot with red highlight on matched "PLAY" text
4. **`click_start_search_FAILED.png`**: Search for "点击开始" button
5. **`click_start_matched_SUCCESS.png`**: Success when "点击开始" button is clicked
6. **`my_collection_search_FAILED.png`**: Search for "我的收藏" button
7. **`my_collection_matched_SUCCESS.png`**: Success when "我的收藏" button is clicked
8. **`hearthstone_collection_reached_SUCCESS.png`**: Final confirmation we're in collection

### Step 3: Compare with Ground Truth

1. Place your PLAY button screenshot in `screenshots/ground_truth/play_button.png`
2. The bot will automatically overlay this image on search screenshots for comparison
3. You can also run the analysis script:
   ```bash
   python analyze_ground_truth.py
   ```
4. This will create analysis images in `screenshots/ground_truth_analysis/`

### Step 4: Understand the Results

The analysis script will show:
- Color ranges that work for your PLAY button
- Most common colors in the image
- Contour detection results

## Common Issues and Solutions

### Issue: Process hanging on exit
**Problem**: The bot process doesn't terminate cleanly when closing the GUI
**Solution**: The bot now includes:
- Aggressive thread termination using ctypes
- 5-second timeout for cleanup operations
- Force exit with `os._exit()` if cleanup fails
- Enhanced pynput keyboard listener cleanup

### Issue: No "PLAY" text detected
**Possible causes:**
- Text is too small or blurry
- OCR confidence is too low
- Text is outside the search region
- Font or color makes text hard to read

**Solutions:**
1. Check the `battlenet_ocr_search_*` screenshot
2. Look at the green search rectangle - is the "PLAY" text inside it?
3. Check if any yellow rectangles are shown around text
4. Verify the text is clear and readable

### Issue: Multiple "PLAY" text candidates
**Possible causes:**
- Multiple instances of "PLAY" text in the search area
- OCR detecting similar text

**Solutions:**
1. The bot clicks the highest confidence candidate
2. Check if the correct text is being clicked
3. Adjust OCR configuration if needed

### Issue: Multiple button candidates
**Possible causes:**
- Multiple blue elements in the search area
- Color detection is too broad

**Solutions:**
1. The bot clicks the first candidate found
2. Check if the correct button is being clicked
3. Adjust color range to be more specific

## Adjusting OCR Configuration

If the bot is not detecting the "PLAY" text correctly, you can adjust the OCR configuration in `ui.py`:

```python
# Current OCR configuration
custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
```

## Adjusting Search Region

If the "PLAY" text is not in the expected location, you can adjust the search region in `ui.py`:

```python
# Current search region (bottom-left 40% of window, bottom 30% area)
search_region_x1 = 0
search_region_y1 = int(window_height * 0.7)
search_region_x2 = int(window_width * 0.4)
search_region_y2 = window_height
```

## Log Messages to Watch For

Look for these key log messages:

**Window Detection Phase:**
- `"Attempt X/10 to find Battle.net window..."`: Retry attempts for window detection
- `"Battle.net window not found on attempt X, waiting 3 seconds..."`: Window not ready yet
- `"Found Battle.net window: ..."`: Battle.net window detection
- `"Battle.net window confirmed - starting PLAY button detection..."`: Window found, starting button search

**Button Detection Phase:**
- `"OCR button detection attempt X/10..."`: Retry attempts for OCR button detection
- `"OCR found X text elements"`: How many text elements OCR detected
- `"Captured Battle.net window screenshot: ..."`: Window screenshot capture
- `"Found PLAY text at (x, y) with confidence X%"`: PLAY text candidates found with confidence scores
- `"Clicking PLAY text at screen coordinates (x, y) with confidence X%"`: Button click confirmation
- `"SUCCESS: Found and clicked PLAY button using OCR!"`: Detection succeeded
- `"Found Hearthstone window: ..."`: Hearthstone verification
- `"Step 1: Looking for '点击开始' (Click to Start) button..."`: Starting Chinese text detection
- `"Found '点击开始' at (x, y) with size (w x h)"`: Chinese button detection
- `"Step 2: Looking for '我的收藏' (My Collection) button..."`: Looking for collection button
- `"Found '我的收藏' at (x, y) with size (w x h)"`: Collection button detection
- `"SUCCESS: Reached Hearthstone collection!"`: Final success confirmation
- `"OCR attempt X: No PLAY text found in search region"`: Detection failed on specific attempt
- `"FAILED: Could not find PLAY button using OCR after 10 attempts"`: Final failure after all retries

**User Control:**
- `"Bot stopped by user during window detection"`: User clicked STOP during window search
- `"Bot stopped by user during button detection"`: User clicked STOP during button search

## Tips for Better Detection

1. **Ensure Battle.net is fully loaded** before the bot tries to detect the button
2. **Check screen resolution** - the bot assumes standard desktop resolution
3. **Verify color settings** - ensure your monitor isn't applying color filters
4. **Use consistent lighting** - avoid dramatic lighting changes
5. **Check for UI updates** - Battle.net interface changes might affect detection

## Getting Help

If you're still having issues:

1. Save the debug screenshots
2. Note the exact log messages
3. Check if the ground truth analysis shows different colors than expected
4. Consider sharing the screenshots (with sensitive information removed) for further analysis

The comprehensive logging should help identify exactly where the detection is failing! 